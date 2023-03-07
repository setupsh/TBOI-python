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

pygame.init()
init_screen()
mixerinit()

class GameMap():
    CHAR_EMPTY = ' '
    CHAR_FULL = 'X'
    CHAR_DOOR = 'D'
    CHAR_PSYCHO = 'P'
    CHAR_CHASER = 'C'
    CHAR_SHOOTER = 'S'
    MAP = (
        level_module.load_level('1level')
    )             
    blocks: List[Block] = list()
    floor_object: List[Block] = list()

    def __init__(self) -> None:
        self.load_map('1level')
        self.create()

    def load_map(self, filename):
        self.MAP = level_module.load_level(filename)

    def create(self):
        enemies.clear()
        for i, e in enumerate(self.MAP):
            for j, c in enumerate(e):
                x = j * Block._size_x
                y = i * Block._size_y
                if c == self.CHAR_FULL:
                    self.blocks.append(Wall([x, y]))
                elif c == self.CHAR_SHOOTER:
                    enemies.add(Shooter((x, y), (48,48), Sprites.normal_enemy, player, projectiles))
                elif c == self.CHAR_CHASER:
                    enemies.add(Chaser((x, y), (48,48), Sprites.hard_enemy, player))
                elif c == self.CHAR_PSYCHO:
                    enemies.add(PsychoMover((x,y), (48,48), Sprites.easy_enemy))        
                self.floor_object.append(Floor([x, y]))

    def draw(self):
        for i in self.floor_object:
            i.draw()    
        for i in self.blocks:
            i.draw()

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

    def check_enemy_collision(player: Player, enemy: Enemy):
        if GameObserver.math_collide(player, enemy):
            enemy.attack(player)

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
        for block in GameMap.blocks:
            if block.can_collide and GameObserver.math_collide(block, player):
                box_cast = GameObject((player._pos_x + player._size_x * 0.5 - 4, player._pos_y + player._size_y * 0.5 - 4), (8, 8), Colors.black)
                match move_direction:
                    case Direction.Left:
                        box_cast._pos_x -= player._size_x * 0.5
                    case Direction.Right:
                        box_cast._pos_x += player._size_x * 0.5
                    case Direction.Up:
                        box_cast._pos_y -= player._size_y * 0.5
                    case Direction.Down:
                        box_cast._pos_y += player._size_y * 0.5
                if GameObserver.math_collide(block, box_cast):
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
        self._game_life_label.set_label(f'{player.health}')

    def draw_game(self):
        self.game_canvas.draw()

    def draw_gameover(self):
        self.gameover_canvas.draw()   

player = Player(start_pos=(scr_width * 0.5, scr_height * 0.5 ), start_size=(50,50), sprite=Sprites.player)
projectiles = Projectiles()
particles = Particles()
enemies = Enemies()

gameui = GameUi()
gamemap = GameMap()

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

    if GameObserver.check_block_collision(gamemap, player, Direction.Left):
        player.bounce(Direction.Right, 1)
    if GameObserver.check_block_collision(gamemap, player, Direction.Right):
        player.bounce(Direction.Left, 1)
    if GameObserver.check_block_collision(gamemap, player, Direction.Up):
        player.bounce(Direction.Down, 1)
    if GameObserver.check_block_collision(gamemap, player, Direction.Down):
        player.bounce(Direction.Up, 1)

    player.update()
    particles.update()
    projectiles.update()                                               
    enemies.update()
    gameui.update()

    gamemap.draw()
    player.draw()
    particles.draw()
    projectiles.draw()
    enemies.draw()

    gameui.draw_game()
    GameObserver.check_projectiles(player, enemies, projectiles)
    GameObserver.enemy_is_killed(enemies, particles)
    if player.is_dead:
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


    


