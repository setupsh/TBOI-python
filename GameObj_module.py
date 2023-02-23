import pygame
import colorlib as Colors
from typing import List, Tuple
from screen_module import *
from enum import Enum
from time_module import Time
from sprite_module import Sprites
import random
import math
import numpy as np

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
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, speed: int, lifetime: float, direction: Direction, shoot_player: bool):
        self.shoot_player = shoot_player
        self.speed = speed
        self.direction = direction
        self.lifetime = lifetime
        self.destroy_on_next_frame = False
        super().__init__(start_pos, start_size, sprite)
    
    def move(self):
        match self.direction:
            case Direction.Up:
                self._pos_y -= self.speed * Time.delta_time 
            case Direction.Down:
                self._pos_y += self.speed * Time.delta_time
            case Direction.Left:
                self._pos_x -= self.speed * Time.delta_time 
            case Direction.Right:
                self._pos_x += self.speed * Time.delta_time                
    
    def reach_down(self) -> bool:
        return self._pos_y > scr_height
    
    def reach_up(self) -> bool:
        return self._pos_y < 0

    def reach_right(self) -> bool:
        return self._pos_x > scr_width

    def reach_left(self) -> bool:
        return self._pos_x < 0    
    
    def update(self):
        self.move()
        if self.reach_down() or self.reach_up() or self.reach_right() or self.reach_left():
            self.destroy_on_next_frame = True
        self.lifetime -= Time.delta_time
        if self.lifetime <= 0:
            self.destroy_on_next_frame = True

class CustomProjectile(Projectile):
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, speed: int, lifetime: float, direction: tuple[int,int], shoot_player: bool):
        super().__init__(start_pos, start_size, sprite, speed, lifetime, direction, shoot_player)

    def move(self):
        self._pos_x += self.direction[0] * self.speed * Time.delta_time
        self._pos_y += self.direction[1] * self.speed * Time.delta_time             


class Projectiles:
    projectiles_list: List[Projectile] = []
    
    def __init__(self) -> None:
        pass                     

    def remove_projectile(self, projectile: Projectile):
        self.projectiles_list.remove(projectile)
    
    def append_projectile(self, projectile: Projectile):
        self.projectiles_list.append(projectile)

    def update(self):
        for i in self.projectiles_list:
            if i.destroy_on_next_frame:
                self.projectiles_list.remove(i)
            else:
                i.update()
    
    def draw(self):
        for i in self.projectiles_list:
            i.draw()


class Player(GameObjSprites):
    health: int = 3
    max_health: int = 3
    is_dead: bool = False 
    # Movement
    _speed: float = 3.0

    # Shooting
    _can_shoot: bool = True
    _cooldown_timer: float = 0.0
    shoot_cooldown: float = 0.3
    bullet_lifetime: float = 0.3
    bullet_speed: int = 500
    bullet_size: int = 25

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

    right_acceleration: float = 0
    def move_right(self):
        self.right_acceleration += Time.delta_time * 2
        if self.right_acceleration >= 1:
            self.right_acceleration = 1

    left_acceleration: float = 0
    def move_left(self):
        self.left_acceleration += Time.delta_time * 2
        if self.left_acceleration >= 1:
            self.left_acceleration = 1

    up_acceleration: float = 0
    def move_up(self):
        self.up_acceleration += Time.delta_time * 2
        if self.up_acceleration >= 1:
            self.up_acceleration = 1

    down_acceleration: float = 0
    def move_down(self):
        self.down_acceleration += Time.delta_time * 2
        if self.down_acceleration >= 1:
            self.down_acceleration = 1

    def get_damage(self, value: int):
        self.health -= value
        self.check_death()  

    def check_death(self):
        if self.health <= 0:
            self.dead()                

    def dead(self):
        self.is_dead = True
        
    def update(self):
        self._pos_x += ((self.right_acceleration) ** 0.5) * self._speed
        self._pos_x -= ((self.left_acceleration) ** 0.5) * self._speed
        self._pos_y += ((self.down_acceleration) ** 0.5) * self._speed
        self._pos_y -= ((self.up_acceleration) ** 0.5) * self._speed
        if self._can_shoot == False:
            self._cooldown_timer -= Time.delta_time
            if self._cooldown_timer <= 0:
                self._can_shoot = True

    def draw(self):
        super().draw()

    def try_shoot(self, direction: Direction, projectiles:Projectiles):
        if self._can_shoot:
            projectiles.append_projectile(Projectile([self._pos_x + self._size_x * 0.5 - self.bullet_size * 0.5 , self._pos_y + self._size_y * 0.5 - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=direction, shoot_player=True))
            self._can_shoot = False
            self._cooldown_timer = self.shoot_cooldown


class Enemy(GameObjSprites):
    health: int = 3
    speed: float = 2.0
    damage: int = 1
    is_dead: bool = False

    target: GameObject = None

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, start_size, sprite)

    def update(self):
        if self.target:
            if self.get_distance_to(self.target) > 50:
                self.move()

    def clamp_number(self, num, a, b):
        return max(min(num, max(a,b)), min(a,b)) 
    
    def smooth_clamp(self, value, min_value, max_value, smooth_factor):
        range_value = max_value - min_value
        clamped_value = max(min(value, max_value), min_value)
        normalized_value = (clamped_value - min_value) / range_value
        smoothed_value = math.pow(normalized_value, smooth_factor)
        return (smoothed_value * range_value) + min_value         

    def smoothclamp(self, x, mi, mx): return mi + (mx-mi)*(lambda t: np.where(t < 0 , 0, np.where( t <= 1 , 3*t**2-2*t**3, 1 ) ) )( (x-mi)/(mx-mi) )

    def set_target(self, new_target: GameObject):
        if new_target:
            self.target = new_target

    def get_distance_to(self, target:GameObject):
        magnitude = ((target._pos_x - self._pos_x) ** 2 + (target._pos_y - self._pos_y) ** 2) ** 0.5
        return(magnitude)
    
    def get_direction_to(self, target:GameObject):
        direction = (target._pos_x - self._pos_x, target._pos_y - self._pos_y)
        return direction    

    def draw(self):
        super().draw()

    def move(self):
        direction = self.get_direction_to(self.target)
        self._pos_x += self.smooth_clamp(direction[0] * self.speed * Time.delta_time, -100, 100, 1)
        self._pos_y += self.smooth_clamp(direction[1] * self.speed * Time.delta_time, -100, 100, 1)

    def attack(self, target: GameObject):
        if type(target) == Player:
            target.get_damage(1)

    def get_damage(self, value: int):
        self.health -= value
        self.check_death()

    def set_speed(self, value: int):
        self.speed = value

    def set_health(self, value: int):
        self.health = value
        self.check_death()

    def check_death(self):
        if self.health <= 0:
            self.is_dead = True               

class PsychoMover(Enemy):
    health: int = 3
    speed: float = 2
    road_to_the_dream: int = 800

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, start_size, sprite)
        self.set_target(self.get_random_point())

    def get_random_point(self) -> GameObject:
        new_target =  GameObject((random.randint(0, scr_width - self._size_x), random.randint(0, scr_height - self._size_y)), (10, 10), Colors.red)
        if self.get_distance_to(new_target) < self.road_to_the_dream:
            new_target = self.get_random_point()
        return new_target     
    
    def update(self):
        if self.target:
            if self.get_distance_to(self.target) > 30:
                self.move()
            else:
                self.set_target(self.get_random_point())  

class Chaser(Enemy):
    health: int = 3
    speed: float = 2
    timer: float = 1
    in_cooldown: bool = False

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, target: GameObject):
        super().__init__(start_pos, start_size, sprite)
        self.set_target(target)     
    
    def update(self):   
        if self.target:
            if self.get_distance_to(self.target) > 30 and not self.in_cooldown:
                self.move()
            else:
                if not self.in_cooldown:
                    self.attack(self.target)
                    self.in_cooldown = True
                else:
                    self.timer -= Time.delta_time
                    if self.timer <= 0:
                        self.in_cooldown = False
                        self.timer = 1

class Shooter(Enemy):
    health: int = 2
    speed: float = 0.1
    timer: float = 0.1
    comeback_time: float = 1.5
    bullet_lifetime: float = 3
    bullet_speed: int = 1
    bullet_size: int = 25
    shoot_trigger_distance: int = 45
    in_cooldown: bool = False

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, target: GameObject, projectiles: Projectiles):
        super().__init__(start_pos, start_size, sprite)
        self.set_target(target)
        self.projectiles = projectiles 

    # ! Я бы использовал его заместо try_shoot
    def attack(self, target: GameObject):
        pass

    def try_shoot(self):
        self.projectiles.append_projectile(CustomProjectile([self._pos_x + self._size_x * 0.5 - self.bullet_size * 0.5 , self._pos_y + self._size_y * 0.5 - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=self.get_direction_to(self.target), shoot_player=False))

    # ! Не нравится алгоритм работы, непонятно зачем используется shoot_trigger_distance.
    def update(self):   
        if self.target:
            self.move()
            if self.get_distance_to(self.target) > self.shoot_trigger_distance and not self.in_cooldown:
               self.try_shoot()
               self.in_cooldown = True     
            else:
                self.timer -= Time.delta_time
                if self.timer <= 0:
                    self.in_cooldown = False
                    self.timer = self.comeback_time

class Enemies():
    enemy_list: List[Enemy] = []

    def __init__(self) -> None:
        pass
    def add(self, enemy: Enemy):
        self.enemy_list.append(enemy)  

    def destroy(self, enemy: Enemy):
        self.enemy_list.remove(enemy)

    def update(self):
        for i in self.enemy_list:
            i.update()
            if i.is_dead:
                self.destroy(i)

    def draw(self):
        for i in self.enemy_list:
            i.draw()





                 
                   






