import pygame
import colorlib as Colors
from typing import List, Tuple
from screen_module import *
from enum import Enum
from time_module import Time
from sprite_module import Sprites


class Direction(Enum):
    Up = 0
    Down = 1
    Right = 2
    Left = 3


class GameObject:   
    _pos_x: int = 0
    _pos_y: int = 0
    _size_x: int = 100
    _size_y: int = 100
    _color: Colors = Colors.black
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], start_color: Colors):
        self.set_position(start_pos)
        self.set_size(start_size)
        self.set_color(start_color)

    def set_position(self,pos:tuple[int, int]):
        self._pos_x = pos[0]
        self._pos_y = pos[1]

    def set_size(self,size: tuple[int, int]):
        self._size_x = size[0]
        self._size_y = size[1]

    def set_color(self,color: tuple[int, int, int]):
        self._color = color           

    rect: pygame.Rect = None
    def draw(self):
        self.rect = pygame.draw.rect(surface=screen, color=self._color, rect=(self._pos_x,
         self._pos_y,
         self._size_x,
         self._size_y ))


class GameObjSprites(GameObject):
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, start_size, Colors.black)
        self.set_sprite(sprite)
        self.set_collider()

    def set_sprite(self, sprite: pygame.image):
        self.sprite = pygame.transform.scale(sprite, (self._size_x, self._size_y))

    def set_collider(self):
        self.collider = pygame.Rect(self._pos_x, self._pos_y, self._size_x, self._size_y)    

    def draw(self):
        self.set_collider()
        screen.blit(self.sprite, self.collider)  


class Particle(GameObjSprites):
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, lifetime: float):
        self.lifetime = lifetime
        super().__init__(start_pos, start_size, sprite)

    def update(self):
        self.lifetime -= Time.delta_time

    def is_alive(self) -> bool:
        return self.lifetime > 0

    def scale(self):
        pygame.transform.scale(self.sprite, (1,1))    

    def draw(self):
       screen.blit(self.sprite) 


class Particles:
    particle_list: List[Particle] = []
    def __init__(self) -> None:
        pass                     

    def remove_particle(self, particle: Particle):
        self.particle_list.remove(particle)

    def update(self):
        for i in self.particle_list:
            i.update()
            if not i.is_alive():
                self.remove_particle(i)

    def append_particle(self, particle: Particle):
        self.particle_list.append(particle)

    def draw(self):
        for i in self.particle_list:
            i.draw()

         
class Projectile(GameObjSprites):
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], speed: int, direction: Direction, shoot_player: bool):
        self.shoot_player = shoot_player
        self.speed = speed
        self.direction = direction
        super().__init__(start_pos, start_size)
    def move(self):
        match self.direction:
            case Direction.Up:
                self._pos_y -= self.speed * Time.delta_time 
            case Direction.Down:
                self._pos_y += self.speed * Time.delta_time
    def reach_down(self) -> bool:
        return self._pos_y > scr_height
    def reach_up(self) -> bool:
        return self._pos_y < 0    


class Projectiles:
    projectiles_list: List[Projectile] = []
    def __init__(self) -> None:
        pass                     

    def remove_projectile(self, projectile: Projectile):
        self.projectiles_list.remove(projectile)
    def move(self):
        for i in self.projectiles_list:
            i.move()
            if i.reach_up() or i.reach_down():
                self.remove_projectile(i)
    def append_projectile(self, projectile: Projectile):
        self.projectiles_list.append(projectile)

    def draw(self):
        for i in self.projectiles_list:
            i.draw()


class Player(GameObjSprites):
    current_speed: float = 0
    speed = float(5)
    right_acceleration: float = 0
    left_acceleration: float = 0
    up_acceleration: float = 0
    down_acceleration: float = 0
    shoot_cooldown = 1
    can_shoot: bool = True

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, start_size, sprite)
            
    def move(self, direction: Direction):
        match direction:      
            case Direction.Left:
                self.move_left()
            case Direction.Right:
                self.move_right()
            case Direction.Up:
                self.move_up()
            case Direction.Down:
                self.move_down()        

    def move_right(self):
        self.right_acceleration += Time.delta_time
        if self.right_acceleration >= 1:
            self.right_acceleration = 1

    def move_left(self):
        self.left_acceleration += Time.delta_time
        if self.left_acceleration >= 1:
            self.left_acceleration = 1

    def move_up(self):
        self.up_acceleration += Time.delta_time
        if self.up_acceleration >= 1:
            self.up_acceleration = 1

    def move_down(self):
        self.down_acceleration += Time.delta_time
        if self.down_acceleration >= 1:
            self.down_acceleration = 1
        

    def update(self):
        self._pos_x += self.right_acceleration * self.speed
        self._pos_x -= self.left_acceleration * self.speed
        self._pos_y += self.down_acceleration * self.speed
        self._pos_y -= self.up_acceleration * self.speed


    def draw(self):
        super().draw()

    def try_shoot(self, projectiles:Projectiles):
        if self.can_shoot:
            projectiles.append_projectile(Projectile([self._pos_x , self._pos_y - 35], [50,50], sprite=Sprites.bullet, speed=100, direction=Direction.Up, shoot_player=True))


class Enemy(GameObjSprites):
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, health: int = 1):
        super().__init__(start_pos, start_size, sprite)
    def draw(self):
        super().draw()
    def move(self, direction:Direction, step: int):
        match direction:
            case Direction.Left: self._pos_x -= step
            case Direction.Right: self._pos_x += step
            case Direction.Down: self._pos_y += step
            case Direction.Up: self._pos_y -= step    

#class Enemies():
#    enemy_list: List[Enemy] = []
#
#    def __init__(self, start_pos: Tuple[int, int],start_size: Tuple[int,int], enemy_in_row: int, enemy_in_column: int,steps: int, distance : int, enemy_sprite: pygame.image) -> None:
#        self._path_length = scr_width - (enemy_in_row * distance)
#        self.start_x = self.x = start_pos[0]
#        self.direction = Direction.Right
#        self.x = start_pos[0]
#        self.y = start_pos[1]
#        self.steps = steps
#        self.distance = distance
#        for c in range(0, enemy_in_column):
#            for r in range(0, enemy_in_row):
#                new_pos = [start_pos[0] + r * distance, start_pos[1] + c * distance]
#                new_enemy = Enemy(new_pos, start_size, random.choice(Sprites.list_enemies))
#                self.enemy_list.append(new_enemy)
#       
#    def _reach_right_board(self) -> bool:
#        return self.x >= self.start_x + self._path_length + self.distance // 2
#        
#    def _reach_left_board(self) -> bool:
#        return self.x <= self.start_x
#    def destroy(self, obj):
#        self.enemy_list.remove(obj)
#    def move(self):
#        match self.direction:
#            case Direction.Left: self.move_left()
#            case Direction.Right: self.move_right()
#
#        for enemy in self.enemy_list:
#            enemy.move(self.direction, self.steps)
#
#    def move_right(self):
#        self.x += self.steps
#        if self._reach_right_board():
#            self.direction = Direction.Left
#            for enemy in self.enemy_list:
#                enemy.move(Direction.Down, 20)
#
#    def move_left(self):
#        self.x -= self.steps
#        if self._reach_left_board():
#            self.direction = Direction.Right
#            for enemy in self.enemy_list:
#                enemy.move(Direction.Down, 20)
#
#    def draw(self):
#        for i in self.enemy_list:
#            i.draw()





                 
                   






