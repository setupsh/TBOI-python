import math
from typing import List
import pygame
import random
import colorlib as Colors
from time_module import Time
from events_module import Inpunting
from events_module import get as get_events
from screen_module import * 
from screen_module import init as init_screen
from GameObj_module import *
from GUI_module import GuiLabel, Canvas, HorizontalAlignment, VerticalAlignment, obvodka, Button
from sounds_module import init as mixerinit, Sound, Sounds, Music, Tracks
from sprite_module import Sprites, BackGrounds
import level_module
from level_module import Level, Room

pygame.init()
init_screen()
mixerinit()

class GameMap():
    
    @property 
    def player(self): return self.current_room.player

    @property
    def enemies(self): return self.current_room.enemies
    
    @property 
    def particles(self): return self.current_room.particles

    @property 
    def projectiles(self): return self.current_room.projectiles

    def __init__(self) -> None:
        self.current_level = Level(expand_iterations=2)
        self.current_room = self.current_level.get_room(0)

    def goto_next_room(self, direction: Direction):
        self.current_room = self.current_level.get_next_room(self.current_room, direction)

    def teleport_player_to_door(self,  direction: Direction):
        self.player.stop_inertion()
        match direction:
            case Direction.Left:
                self.player.set_position([scr_width - 112, scr_height * 0.5 - self.player._size_x * 0.5])
            case Direction.Right:
                self.player.set_position([64, scr_height * 0.5 - self.player._size_x * 0.5])
            case Direction.Up:
                self.player.set_position([scr_width * 0.5 - self.player._size_x * 0.5, scr_height - 112])
            case Direction.Down:
                self.player.set_position([scr_width * 0.5 - self.player._size_x * 0.5, 64])           

    def update(self):
        self.current_room.update()

    def draw(self):
        self.current_room.draw()

#Наблюдатель
class GameObserver:
    secs: float = 0
    timer: int = 0

    game_is_active: bool = True
    game_is_paused: bool = False
    game_is_over: bool = False
    player_is_win: bool = False

    def restart_game():
        GameObserver.reset_game()
        GameObserver.launch_game()
    def launch_game():
        GameObserver.game_is_active = True
        GameObserver.game_is_paused = False
    def stop_game():
        GameObserver.game_is_active = False  
    def pause_game():
        GameObserver.game_is_paused = True                        
    def continue_game():
        GameObserver.game_is_paused = False          
    def reset_game():
        GameObserver.game_is_active = False
        GameObserver.game_is_paused = False
        GameObserver.timer = 0
        GameObserver.game_is_over = False
    def game_over():
        GameObserver.game_is_over = True
        Sound.PlayOne(Sounds.Horse)

    def rect_collide(rect: pygame.Rect, rect2: pygame.Rect) -> bool:
        if not rect or not rect2: return False 
        return rect.colliderect(rect2.left, rect2.top, rect2.width, rect2.height)
    
    def math_collide(GO1, GO2):
        return (GO1._pos_x + GO1._size_x >= GO2._pos_x) and (GO1._pos_x < GO2._pos_x + GO2._size_x) and (GO1._pos_y + GO1._size_y >= GO2._pos_y) and (GO1._pos_y < GO2._pos_y + GO2._size_y)    

    def check_projectiles(player: Player, enemies: Enemies, projectiles: Projectiles):
        for projectile in projectiles.projectiles_list:
            if projectile.shoot_player:
                for enemy in enemies.enemy_list:
                    if GameObserver.math_collide(enemy, projectile):
                        projectiles.remove_projectile(projectile)
                        enemy.get_damage(1)
            else:               
                if GameObserver.math_collide(player, projectile):
                    projectiles.remove_projectile(projectile)
                    player.get_damage(1)        

    def enemy_is_killed(enemies: Enemies, particles: Particles):
        for enemy in enemies.enemy_list:
            if enemy.is_dead:
                particles.append_particle(Skull ([enemy._pos_x, enemy._pos_y], [50,50]))

    def check_block_collision(gamemap: GameMap, player: Player, move_direction: Direction):
        for block in gamemap.current_room.blocks:
            if block.can_collide and GameObserver.math_collide(block, player):
                box_cast = GameObject((player._pos_x + player._size_x * 0.5, player._pos_y + player._size_y * 0.5), (8, 8), Colors.black)
                match move_direction:
                    case Direction.Left:
                        box_cast._pos_x -= player._size_x
                    case Direction.Right:
                        box_cast._pos_x += player._size_x
                    case Direction.Up:
                        box_cast._pos_y -= player._size_x
                    case Direction.Down:
                        box_cast._pos_y += player._size_x
                if GameObserver.math_collide(block, box_cast):
                    if type(block) == Door and gamemap.current_room.is_cleared:
                        block: Door
                        gamemap.goto_next_room(block.direction)
                        gamemap.teleport_player_to_door(block.direction)
                    return True
        return False                        

class GameUi:
    _labelFont = pygame.font.SysFont('Arial', 18)
    #TODO: Очки и здоровье
    game_canvas: Canvas = Canvas()
    gameover_canvas: Canvas = Canvas()

    _gameover_title: GuiLabel = GuiLabel ([scr_width/2,scr_height/2], 'Ты проиграл', Colors.white)
    _game_life_label: GuiLabel = GuiLabel([0,0], f'score ', Colors.white, horizontal = HorizontalAlignment.Left, vertical = VerticalAlignment.Top)

    def __init__(self) -> None:
        self.gameover_canvas.extend_el([self._gameover_title])
        self.game_canvas.extend_el([self._game_life_label])
    def update(self):
        self._game_life_label.set_label(f'{gamemap.player.health} {gamemap.current_room.id}')

    def draw_game(self):
        self.game_canvas.draw()

    def draw_gameover(self):
        self.gameover_canvas.draw()

gameui = GameUi()
gamemap = GameMap()

def game_loop():
    screen.fill(Colors.black)
    GameObserver.secs += Time.delta_time
    GameObserver.timer = int(GameObserver.secs)

    if (Inpunting.is_key_a_pressed):
        gamemap.player.move(Direction.Left)
    else:    
        gamemap.player.left_acceleration -= Time.delta_time * 3
        if gamemap.player.left_acceleration < 0:
            gamemap.player.left_acceleration = 0
    
    if (Inpunting.is_key_d_pressed):
        gamemap.player.move(Direction.Right)
    else:
        gamemap.player.right_acceleration -= Time.delta_time * 3
        if gamemap.player.right_acceleration < 0:
            gamemap.player.right_acceleration = 0

    if (Inpunting.is_key_w_pressed):
        gamemap.player.move(Direction.Up)
    else:
        gamemap.player.up_acceleration -= Time.delta_time * 3
        if gamemap.player.up_acceleration < 0:
            gamemap.player.up_acceleration = 0        

    if (Inpunting.is_key_s_pressed):
        gamemap.player.move(Direction.Down)
    else:
        gamemap.player.down_acceleration -= Time.delta_time * 3
        if gamemap.player.down_acceleration < 0:
            gamemap.player.down_acceleration = 0       
        
    if (Inpunting.is_key_up_pressed):
        gamemap.player.try_shoot(Direction.Up, gamemap.projectiles)

    if (Inpunting.is_key_down_pressed):
        gamemap.player.try_shoot(Direction.Down, gamemap.projectiles)

    if (Inpunting.is_key_left_pressed):
        gamemap.player.try_shoot(Direction.Left, gamemap.projectiles)

    if (Inpunting.is_key_right_pressed):      
        gamemap.player.try_shoot(Direction.Right, gamemap.projectiles)               

    if GameObserver.check_block_collision(gamemap, gamemap.player, Direction.Left):
        gamemap.player.bounce(Direction.Right, 0.4)
    if GameObserver.check_block_collision(gamemap, gamemap.player, Direction.Right):
        gamemap.player.bounce(Direction.Left, 0.4)
    if GameObserver.check_block_collision(gamemap, gamemap.player, Direction.Up):
        gamemap.player.bounce(Direction.Down, 0.4)
    if GameObserver.check_block_collision(gamemap, gamemap.player, Direction.Down):
        gamemap.player.bounce(Direction.Up, 0.4)

    gamemap.update()
    gameui.update()
    
    gamemap.draw()
    gameui.draw_game()

    GameObserver.check_projectiles(gamemap.player, gamemap.enemies, gamemap.projectiles)
    GameObserver.enemy_is_killed(gamemap.enemies, gamemap.particles)
    if gamemap.player.is_dead:
        GameObserver.game_is_over = True

def game_over_loop():
    screen.fill(Colors.black)
    gameui.draw_gameover()  

def main_menu_loop():
    screen.fill(Colors.black)
    print(1)

def win_screen_loop():
    screen.fill(Colors.black)
    gameui.draw_win()

while True:
    get_events()

    if GameObserver.game_is_active:
        if not GameObserver.game_is_paused:
            if not GameObserver.player_is_win:
                if not GameObserver.game_is_over:
                    game_loop()
                
                else: game_over_loop()
            else:
                win_screen_loop()    
        else:
            pass
    else:
        main_menu_loop()
    
    pygame.display.update()  
    Time.update()