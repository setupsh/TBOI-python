import pygame
import colorlib as Colors
from typing import List, Tuple, Set
from screen_module import *
from enum import Enum
from time_module import Time
from sprite_module import Sprites
import random
import math
import numpy as np
from animation_module import *

class Direction(Enum):
    Up = 0
    Down = 1
    Right = 2
    Left = 3

class GameObject:   
    _pos_x: int = 0
    _pos_y: int = 0
    _size_x: int = 48
    _size_y: int = 48
    _color: Colors = Colors.black

    @property
    def x(self): return self._pos_x + self._size_x * 0.5
    @property
    def y(self): return self._pos_y + self._size_y * 0.5

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


class Skull(Particle):
    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int]):
        super().__init__(start_pos, start_size, Sprites.death_skull, 9999)
    def update(self):
        self.set_sprite(Sprites.death_skull)
        return super().update()

class Particles:
    def __init__(self) -> None:                     
        self.particle_list: List[Particle] = []

    def remove_particle(self, particle: Particle):
        self.particle_list.remove(particle)

    def update(self):
        for i in self.particle_list:
            i.update()
            if not i.is_alive():
                self.remove_particle(i)

    def append_particle(self, particle: Particle):
        self.particle_list.append(particle)

    def clear(self):
        self.particle_list.clear()     

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
        self.magnitude = self.get_magnitude()

    def get_distance_to(self, target:tuple[int,int]):
        magnitude = ((target[0] - self.x) ** 2 + (target[1] - self.y) ** 2) ** 0.5
        return(magnitude)
    def get_magnitude(self):
        magnitude = self.get_distance_to(self.direction)
        if (magnitude <= 50 or magnitude == 0):
            magnitude = 1
        print(magnitude)    
        return magnitude
    def move(self):
        self._pos_x += (self.direction[0] / self.magnitude) * self.speed * Time.delta_time
        self._pos_y += (self.direction[1] / self.magnitude) * self.speed * Time.delta_time

    def draw(self):
        super().draw()

class Projectiles:
    
    def __init__(self) -> None:                     
        self.projectiles_list: List[Projectile] = []

    def remove_projectile(self, projectile: Projectile):
        if projectile in self.projectiles_list:
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
    health: int = 5
    max_health: int = 5
    is_dead: bool = False 
    in_invicible: bool = False
    invivible_timer: float = 1
    invicible_timer_comeback = 1
    lifes: int = 0
    companion = None
    active_buff = None
    super_cheater_kill = False 
    # Movement
    _speed: float = 3.0

    # Shooting
    _can_shoot: bool = True
    _cooldown_timer: float = 0.0
    shoot_cooldown: float = 0.3
    bullet_lifetime: float = 0.3
    bullet_speed: int = 500
    bullet_size: int = 25
    bullet_percing: bool = False

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, start_size, sprite)

    def set_position(self, pos: tuple[int, int]):
        if self.companion:
            self.companion.set_position(pos)
        return super().set_position(pos)    
            
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
        if not self.in_invicible:
            self.health -= value
        self.check_death()
        self.in_invicible = True

    def check_death(self):
        if self.health <= 0:
            self.dead()

    def dead(self):
        self.is_dead = True

    def revive(self):
        self.set_hp(3)
        self.in_invicible = True
        self.lifes -= 1
        self.is_dead = False
    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def set_hp(self, amount):
        self.health = amount
        if self.health > self.max_health:
            self.health = self.max_health

    def set_active_buff(self, active_buff):
        self.active_buff: ActiveBuff = active_buff

    def set_companion(self, companion):
        self.companion: Companion = companion    

    def bullet_change(self, firerate: int = 1, size: int = 1, range: int = 1, shootspeed: int = 1):
        self.shoot_cooldown *= firerate if firerate > 0 else 1
        self.bullet_size *= size if size > 0 else 1
        self.bullet_lifetime *= range if range > 0 else 1
        self.bullet_speed *= shootspeed if shootspeed > 0 else 1
        
    def update(self):
        self._pos_x += ((self.right_acceleration) ** 0.5) * self._speed
        self._pos_x -= ((self.left_acceleration) ** 0.5) * self._speed
        self._pos_y += ((self.down_acceleration) ** 0.5) * self._speed
        self._pos_y -= ((self.up_acceleration) ** 0.5) * self._speed
        if self._can_shoot == False:
            self._cooldown_timer -= Time.delta_time
            if self._cooldown_timer <= 0:
                self._can_shoot = True

        if self.in_invicible:
            self.invivible_timer -= Time.delta_time
            if self.invivible_timer <= 0:
                self.in_invicible = False
                self.invivible_timer = self.invicible_timer_comeback
        if self.companion:
            self.companion.update()        

        # TODO куллдаун неузвимовсти (аналогично верхнему условия)

    def draw(self):
        if self.companion:
            self.companion.draw()
        super().draw()

    def try_shoot(self, direction: Direction, projectiles:Projectiles):
        if self._can_shoot:
            projectiles.append_projectile(Projectile([self.x - self.bullet_size * 0.5 , self.y - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=direction, shoot_player=True))
            self._can_shoot = False
            self._cooldown_timer = self.shoot_cooldown
        if self.companion and self.companion.can_shoot:
            self.companion.try_shoot(direction, projectiles)    

class Enemy(GameObjSprites):
    health: int = 3
    speed: int = 100
    damage: int = 1
    is_dead: bool = False

    target: GameObject = None

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, start_size, sprite)

    def update(self):
        if self.target:
            if self.get_distance_to(self.target) > 50:
                self.move()

    def set_target(self, new_target: GameObject):
        if new_target:
            self.target = new_target

    def get_distance_to(self, target:GameObject):
        magnitude = ((target.x - self.x) ** 2 + (target.y - self.y) ** 2) ** 0.5
        return(magnitude)
    
    def get_direction_to(self, target:GameObject):
        direction = (target.x - self.x, target.y - self.y)
        return direction    

    def draw(self):
        super().draw()

    def move(self):
        direction = self.get_direction_to(self.target)
        magnitude = self.get_distance_to(self.target)
        self._pos_x += (direction[0] / magnitude) * self.speed * Time.delta_time
        self._pos_y += (direction[1] / magnitude) * self.speed * Time.delta_time

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

    def kill(self):
        self.is_dead = True
        Vampirism.increase_kill_count()    

    def check_death(self):
        if self.health <= 0:
            self.kill()              

class PsychoMover(Enemy):
    health: int = 3
    speed: float = 100
    road_to_the_dream: int = 300

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, target_to_beat: GameObject):
        self.target_to_beat = target_to_beat
        super().__init__(start_pos, start_size, sprite)
        self.animator = Animator((self.sprite, Sprites.fun_ghost), (Sprites.door, Sprites.wizard), (self.sprite))
        self.set_target(self.get_random_point())
        self.animator.set_animation(Sequences.Walk)

    def get_random_point(self) -> GameObject:
        new_target =  GameObject((random.randint(0, scr_width - self._size_x), random.randint(0, scr_height - self._size_y)), (10, 10), Colors.red)
        if self.get_distance_to(new_target) < self.road_to_the_dream:
            new_target = self.get_random_point()
        return new_target     
    
    def update(self):
        if self.animator.update():
            self.set_sprite(self.animator.get_updated_frame())
        if self.target:
            if self.get_distance_to(self.target) > 30:
                self.move()
            else:
                self.set_target(self.get_random_point()) 
                   
            if self.get_distance_to(self.target_to_beat) < 30:
                self.attack(self.target_to_beat)

class Chaser(Enemy):
    health: int = 3
    speed: float = 100
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
    speed: float = 100
    comeback_time: float = 1.5
    timer = comeback_time
    bullet_lifetime: float = 3
    bullet_speed: int = 500
    bullet_size: int = 25
    shoot_trigger_distance: int = 400
    in_cooldown: bool = True

    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, target: GameObject, projectiles: Projectiles):
        super().__init__(start_pos, start_size, sprite)
        self.set_target(target)
        self.projectiles = projectiles 

    def attack(self, target: GameObject):
        pass

    def try_shoot(self):
        self.projectiles.append_projectile(CustomProjectile([self.x - self.bullet_size * 0.5 , self.y - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=self.get_direction_to(self.target), shoot_player=False))

    def update(self):   
        if self.target:
            if self.get_distance_to(self.target) > self.shoot_trigger_distance:
                self.move()

            elif not self.in_cooldown:
               self.try_shoot()
               self.in_cooldown = True 

            else:
                self.timer -= Time.delta_time
                if self.timer <= 0:
                    self.in_cooldown = False
                    self.timer = self.comeback_time
class Enemies():
    
    def __init__(self) -> None:
        self.enemy_list: List[Enemy] = []

    def add(self, enemy: Enemy):
        self.enemy_list.append(enemy)  

    def clear(self):
        self.enemy_list.clear()    

    def destroy(self, enemy: Enemy):
        self.enemy_list.remove(enemy)

    def kill_all(self):
        for enemy in self.enemy_list:
            enemy.is_dead = True    

    def update(self):
        for i in self.enemy_list:
            i.update()
            if i.is_dead:
                self.destroy(i)

    def draw(self):
        for i in self.enemy_list:
            i.draw()

class Block(GameObjSprites):
    defualt_sprite: pygame.image = None
    can_collide: bool = True
    def __init__(self, start_pos: tuple[int, int], sprite: pygame.image):
        super().__init__(start_pos, [48,48], sprite)

class Wall(Block):
    defualt_sprite: pygame.image = Sprites.block
    def __init__(self, start_pos: tuple[int, int]):
        super().__init__(start_pos, self.defualt_sprite)

class Floor(Block):
    defualt_sprite: pygame.image = Sprites.floor
    can_collide = False
    def __init__(self, start_pos: tuple[int, int]):
        super().__init__(start_pos, self.defualt_sprite)

class Door(Block):
    defualt_sprite: pygame.image = Sprites.door

    @property
    def alternative_direction(self):
        match self.direction:
            case Direction.Up: return Direction.Down 
            case Direction.Down: return Direction.Up 
            case Direction.Right: return Direction.Left 
            case Direction.Left: return Direction.Right
        return Direction.Up  
       
    def __init__(self, start_pos: tuple[int, int], start_direction: Direction):
        super().__init__(start_pos, self.defualt_sprite)
        self.direction = start_direction

class Buff(GameObjSprites):
    defualt_sprite: pygame.image = None
    def __init__(self, start_pos: tuple[int, int], sprite: pygame.image, target: Player):
        super().__init__(start_pos, [48,48], sprite) 
        self.target = target

    def apply():
        pass

class Buffs():
    def __init__(self) -> None:
        self.buff_list: List[Buff] = []

    def remove_projectile(self, buff: Buff):
        if buff in self.buff_list:
            self.buff_list.remove(buff)   
    
    def append_projectile(self, buff: Buff):
        self.buff_list.append(buff)

    def draw(self):
        for i in self.buff_list:
            i.draw()

class MedKit(Buff):
    defualt_sprite: pygame.image = Sprites.medkit
    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)

    def apply(self):
        self.target.heal(3)

class RPG7(Buff):
    defualt_sprite: pygame.image = Sprites.RPG7
    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)

    def apply(self):
        self.target.bullet_change(firerate=0.7, size=1.5)
        self.target.bullet_percing = True

class FunGhost(Buff):
    defualt_sprite: pygame.image = Sprites.fun_ghost
    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)

    def apply(self):
        self.target._speed += 0.5 

class LIFEUP(Buff):
    defualt_sprite: pygame.image = Sprites.LIFEUP
    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)
    def apply(self):
        self.target.lifes += 1

class Vampirism(Buff):
    kill_counter: int = 0
    is_active: bool = False
    target: Player = None
    defualt_sprite: pygame.image = Sprites.Vampirism
    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)
        Vampirism.target = target
    def apply(self):
        Vampirism.is_active = True
    def heal(self):
        self.target.heal(1)    
    @classmethod
    def increase_kill_count(cls):
        if cls.is_active:
            cls.kill_counter += 1
            if cls.kill_counter >= 10:
                cls.target.heal(1)

class ActiveBuff(Buff):
    defualt_sprite: pygame.image = Sprites.door
    name: str = 'Name'
    needed_charges = int
    current_charges = needed_charges
    def __init__(self, start_pos: tuple[int, int], defualt_sprite: pygame.image, target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)

    @classmethod
    def use(cls):
        pass

    @classmethod
    def charge(cls, amount):
        cls.current_charges += amount
        if cls.current_charges > cls.needed_charges:
            cls.current_charges = cls.needed_charges

class DeadDetonator(ActiveBuff):
    defualt_sprite: pygame.image = Sprites.DeadDetonator
    name = 'DeadDetonator'
    needed_charges = 4
    current_charges = needed_charges
    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)
        DeadDetonator.target = target
    def apply(self):
        DeadDetonator.target.set_active_buff(DeadDetonator)
        DeadDetonator.charge(DeadDetonator.needed_charges)
    @classmethod        
    def use(cls):
        if cls.current_charges >= cls.needed_charges:
            cls.target.heal(1) 
            cls.current_charges = 0

class Companion(Buff):
    can_shoot: bool = False
    def __init__(self, start_pos: tuple[int, int], sprite: pygame.image, target: Player):
        self.target = target
        super().__init__(start_pos, sprite , target)

    def apply(self):
        self.target.set_companion(Companion((self.target._pos_x, self.target._pos_y), self.target))

    def set_target(self, new_target: GameObject):
        if new_target:
            self.target = new_target

    def get_distance_to(self, target:GameObject):
        magnitude = ((target.x - self.x) ** 2 + (target.y - self.y) ** 2) ** 0.5
        return(magnitude)
        
    def get_direction_to(self, target:GameObject):
        direction = (target.x - self.x, target.y - self.y)
        return direction
    
    def move(self):
        pass

    def update(self):
        pass        


class Companion_Shooter(Companion):
    defualt_sprite: pygame.image = Sprites.wizard
    speed: float = 1

    can_shoot: bool = True
    cooldown_timer: float = 0.0
    shoot_cooldown: float = 0.3
    bullet_lifetime: float = 0.3
    bullet_speed: int = 500
    bullet_size: int = 25

    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)
        self.target = target

    def apply(self):
        self.target.set_companion(Companion_Shooter((self.target.x, self.target.y), self.target))

    def try_shoot(self, direction: Direction, projectiles:Projectiles):
        if self.can_shoot:
            projectiles.append_projectile(Projectile([self.x - self._size_y * 0.5 , self.y - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=direction, shoot_player=True))
            self.can_shoot = False
            self.cooldown_timer = self.shoot_cooldown    

    def move(self):
        direction = self.get_direction_to(self.target)
        self._pos_x += direction[0] * self.speed * Time.delta_time
        self._pos_y += direction[1] * self.speed * Time.delta_time

    def update(self):
        if self.get_distance_to(self.target) >= 40:
            self.move()
        if self.can_shoot == False:
            self.cooldown_timer -= Time.delta_time
            if self.cooldown_timer <= 0:
                self.can_shoot = True

class Orbital(Companion):
    defualt_sprite: pygame.image = Sprites.bullet

    x = -100
    r = x ** 2
    f = lambda x: (Orbital.r - x ** 2) ** 0.5
    down_up: bool = True

    def __init__(self, start_pos: tuple[int, int], target: Player):
        super().__init__(start_pos, self.defualt_sprite, target)

    def apply(self):
        self.target.set_companion(Orbital((self.target.x, self.target.y), self.target))    

    def move(self):
        if self.down_up:
            self.x += 1
            y = Orbital.f(self.x)
            self.set_position((self.x + self.target._pos_x, y + self.target._pos_y))
            if self.x >= self.r ** 0.5:
                self.down_up = False
        else:
            self.x -= 1
            y = -Orbital.f(self.x)
            self.set_position((self.x + self.target._pos_x, y + self.target._pos_y))
            if self.x <= -self.r ** 0.5:
                self.down_up = True

    def update(self):
        self.move()                

class TheBoss(Enemy):
    health = 30
    speed: float = 300
    bullet_lifetime: float = 3
    bullet_speed: int = 1
    bullet_size: int = 25
    in_cooldown: bool = False
    cooldown_timer: float = 2
    cooldown_timer_comeback = 2
    dash_timer: float = 1
    dash_timer_comeback: float = 1
    in_dash: bool = False


    def __init__(self, start_pos: tuple[int, int], start_size: tuple[int, int], sprite: pygame.image, target: Player, projectiles: Projectiles, enemies: Enemies):
        self.target = target
        self.projectiles = projectiles
        self.enemies = enemies
        self.dash_point = self.get_dash_point()
        super().__init__(start_pos, start_size, sprite)

    def move(self):
        magnitude = self.get_distance_to(self.dash_point)
        direction = self.get_direction_to(self.dash_point)
        self._pos_x += (direction[0] / magnitude) * self.speed * Time.delta_time
        self._pos_y += (direction[1] / magnitude) * self.speed * Time.delta_time

    def get_dash_point(self) -> GameObject:
        new_target =  GameObject((self.target.x, self.target.y), (10, 10), Colors.red)
        return new_target         

    def shoot_line(self):
        for i in range(5):
            self.projectiles.append_projectile(CustomProjectile([self.x - self.bullet_size * 0.5 , self.y - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=self.get_direction_to(self.target), shoot_player=False))

    def shoot_around(self):
        direction: int = 0
        for i in range(8):
            direction += 1
            self.projectiles.append_projectile(Projectile([self.x - self.bullet_size * 0.5 , self.y - self.bullet_size * 0.5], [self.bullet_size,self.bullet_size], sprite=Sprites.bullet, speed=self.bullet_speed, lifetime=self.bullet_lifetime, direction=direction, shoot_player=False))
            if direction >= 4:
                direction = 0

    def summon(self):
        self.enemies.add(Chaser((self.x, self.y), (48,48), Sprites.Boss_summon, self.target))

    def dash(self):
        self.dash_point = self.get_dash_point()
        self.in_dash = True    

    def random_action(self):
        random_number = random.randint(1, 10)
        if random_number < 2:
            self.summon()
        elif random_number < 6:
            self.dash()
        elif random_number < 8:
            self.shoot_around()
        else:
            self.shoot_line()    

    def update(self):
        if not self.in_cooldown:
            self.random_action()
            self.in_cooldown = True

        if self.in_cooldown:
            self.cooldown_timer -= Time.delta_time
            if self.cooldown_timer <= 0:
                self.in_cooldown = False
                self.cooldown_timer = self.cooldown_timer_comeback

        if self.get_distance_to(self.target) < 50:
            self.attack(self.target)

        if self.in_dash:
            self.dash_timer -= Time.delta_time
            self.move()
            if self.dash_timer <= 0:
                self.in_dash = False
                self.dash_timer = self.dash_timer_comeback
                self.in_cooldown = True

    def draw(self):
        super().draw()
        self.dash_point.draw()             


    












    
        
