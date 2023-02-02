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

pygame.init()
init_screen()
mixerinit()

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
        return (GO1._pos_x >= GO2._pos_x) and (GO1._pos_x < GO2._pos_x + GO2._size_x) and (GO1._pos_y >= GO2._pos_y) and (GO1._pos_y < GO2._pos_y + GO2._size_y)    

    def check_enemy_collision(player: Player, enemy: Enemy):
        if GameObserver.math_collide(player, enemy):
            enemy.attack(player)
        
class GameUi:
    _labelFont = pygame.font.SysFont('Arial', 18)
    #TODO: Очки и здоровье
    game_canvas: Canvas = Canvas()

    def __init__(self) -> None:
        pass
    def update(self):
        pass
    def draw_game(self):
        pass 

enemy = PsychoMover([80,80], [50,50], Sprites.easy_enemy)
projectiles = Projectiles()
player = Player(start_pos=(scr_width * 0.5, scr_height * 0.9 ), start_size=(50,50), sprite=Sprites.player)
gameui = GameUi()

def game_loop():
    screen.fill(Colors.black)
    GameObserver.secs += Time.delta_time
    GameObserver.timer = int(GameObserver.secs)

    if (Inpunting.is_key_a_pressed):
        player.move(Direction.Left)
    else:
        player.left_acceleration -= Time.delta_time * 3
        if player.left_acceleration < 0:
            player.left_acceleration = 0

    if (Inpunting.is_key_d_pressed):
        player.move(Direction.Right)
    else:
        player.right_acceleration -= Time.delta_time * 3
        if player.right_acceleration < 0:
            player.right_acceleration = 0

    if (Inpunting.is_key_w_pressed):
        player.move(Direction.Up)
    else:
        player.up_acceleration -= Time.delta_time * 3
        if player.up_acceleration < 0:
            player.up_acceleration = 0        

    if (Inpunting.is_key_s_pressed):
        player.move(Direction.Down)
    else:
        player.down_acceleration -= Time.delta_time * 3
        if player.down_acceleration < 0:
            player.down_acceleration = 0       

    if (Inpunting.is_key_up_pressed):
        player.try_shoot(Direction.Up, projectiles)

    if (Inpunting.is_key_down_pressed):
        player.try_shoot(Direction.Down, projectiles)

    if (Inpunting.is_key_left_pressed):
        player.try_shoot(Direction.Left, projectiles)

    if (Inpunting.is_key_right_pressed):
        player.try_shoot(Direction.Right, projectiles)  

    enemy.draw()
    projectiles.update()                                               
    projectiles.draw()
    player.update()
    player.draw()
    GameObserver.check_enemy_collision(player, enemy)

def game_over_loop():
    screen.fill(Colors.black)
    gameui.draw_gameover()
    GameObserver.stop_game()
    print(1)

def main_menu_loop():
    screen.fill(Colors.black)

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


    


