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
from level_module import Room, Level

pygame.init()
init_screen()
mixerinit()

class GameMap():

    @property
    def player(self): return self.current_room.player
    @property
    def enemies(self): return self.current_room.enemies
    @property
    def projectiles(self): return self.current_room.projectiles
    @property
    def particles(self): return self.current_room.particles
    @property
    def buffs(self): return self.current_room.buffs

    def __init__(self) -> None:
        self.current_level = Level(iterartion=1)
        self.current_room = self.current_level.get_room(0)
    
    def go_to_next_room(self, direction: Direction):
        gamemap.current_room.discovered = True
        self.current_room = self.current_level.get_next_room(self.current_room, direction)
        if self.player.super_cheater_kill:
            self.enemies.kill_all()
            
    def player_teleport_door(self, direction: Direction):
        if not gamemap.current_room.discovered and gamemap.player.active_buff:
            gamemap.player.active_buff.charge(1)            
        match direction:      
            case Direction.Left:
                self.player.set_position([scr_width - 97 , scr_height * 0.5 - self.player._size_x * 0.5])
            case Direction.Right:
                self.player.set_position([49 , scr_height * 0.5 - self.player._size_x * 0.5])
            case Direction.Up:
                self.player.set_position([scr_width * 0.5 - self.player._size_x * 0.5 , scr_height - 97])
            case Direction.Down:
                self.player.set_position([scr_width * 0.5 - self.player._size_x * 0.5 , 49])           
                
    def draw(self):
        self.current_room.draw()
    def update(self):
        self.current_room.update()

class DebugConsole():
    def __init__(self) -> None:
        pass
    def get_command(self):
        command = input().split()
        #value = input()
        self.execute_command(command)

    def execute_command(self, command):
        if command.__len__() == 2:
            if command[0] == 'spawnbuff':
                class_name = command[1]
                class_obj = globals()[class_name]
                gamemap.buffs.buff_list.append(class_obj((gamemap.player._pos_x,gamemap.player._pos_y), gamemap.player))    

            elif command[0] == 'debug':
                is_applied_1 = False
                is_applied_2 = False

                if command[1] == '1':
                    is_applied_1 = not is_applied_1
                    gamemap.player.max_health = 999 if not is_applied_1 else Player.max_health
                    gamemap.player.health = gamemap.player.max_health
                    
                if command[1] == '2':
                    is_applied_2 = not is_applied_2            
                    gamemap.player.super_cheater_kill = is_applied_2
        elif command.__len__() == 4:
            if command[0] == 'spawnbuff':
                class_name = command[1]
                class_obj = globals()[class_name]
                x = int(command[2])
                y = int(command[3])
                gamemap.buffs.buff_list.append(class_obj((x,y), gamemap.player))            
            
debug_console = DebugConsole()

                
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

    def check_projectiles(player: Player, enemies: Enemies, projectiles: Projectile):
        for projectile in projectiles.projectiles_list:
            if projectile.shoot_player:
                for enemy in enemies.enemy_list:
                    if GameObserver.math_collide(enemy, projectile):
                        if not player.bullet_percing:
                            projectiles.remove_projectile(projectile)
                        enemy.get_damage(1)
            else:               
                if GameObserver.math_collide(player, projectile):
                    projectiles.remove_projectile(projectile)
                    player.get_damage(1) 
            for block in gamemap.current_room.blocks:
                if GameObserver.math_collide(block, projectile):
                    projectiles.remove_projectile(projectile)              

    def enemy_is_killed(enemies: Enemies, particles: Particles):
        for enemy in enemies.enemy_list:
            if enemy.is_dead:
                particles.append_particle(Skull ([enemy._pos_x, enemy._pos_y], [50,50]))

    def buff_collide(buffs: Buffs, player: Player):
        for buff in buffs.buff_list:
            if GameObserver.math_collide(player, buff): 
                buff.apply()
                buffs.buff_list.remove(buff)            

    def player_block_collide(gamemap: GameMap, player: Player, move_direction: Direction):
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
                        gamemap.go_to_next_room(block.direction)
                        gamemap.player_teleport_door(block.direction)
                    return True
                
        return False                       

class GameUi:
    _labelFont = pygame.font.SysFont('Arial', 18)
    #TODO: Очки и здоровье
    game_canvas: Canvas = Canvas()
    gameover_canvas: Canvas = Canvas()

    _gameover_title: GuiLabel = GuiLabel ([scr_width/2,scr_height/2], 'Ты проиграл', Colors.white)
    _game_life_label: GuiLabel = GuiLabel([0,0], f'score ', Colors.white, horizontal = HorizontalAlignment.Left, vertical = VerticalAlignment.Top)
    _active_buff_label: GuiLabel = GuiLabel([scr_width,0], f'', Colors.white, horizontal = HorizontalAlignment.Right, vertical = VerticalAlignment.Top)
    
    def __init__(self) -> None:
        self.gameover_canvas.extend_el([self._gameover_title])
        self.game_canvas.extend_el([self._game_life_label, self._active_buff_label])
    def update(self):
        self._game_life_label.set_label(f'{gamemap.player.health}')
        if gamemap.player.active_buff:
            self._active_buff_label.set_label(f'{gamemap.player.active_buff.name}:{gamemap.player.active_buff.current_charges}')

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

    if (Inpunting.is_key_space_pressed) and gamemap.player.active_buff:
        gamemap.player.active_buff.use()

    if (Inpunting.is_key_tilda_pressed):
        debug_console.get_command()           

    if GameObserver.player_block_collide(gamemap, gamemap.player, Direction.Left):
        gamemap.player.left_acceleration = 0
    if GameObserver.player_block_collide(gamemap, gamemap.player, Direction.Right):
        gamemap.player.right_acceleration = 0    
    if GameObserver.player_block_collide(gamemap, gamemap.player, Direction.Up):
        gamemap.player.up_acceleration = 0    
    if GameObserver.player_block_collide(gamemap, gamemap.player, Direction.Down):
        gamemap.player.down_acceleration = 0                 

    gamemap.update()
    gameui.update()
    
    gamemap.draw()
    gameui.draw_game()
    
    GameObserver.check_projectiles(gamemap.player, gamemap.enemies, gamemap.projectiles)
    GameObserver.enemy_is_killed(gamemap.enemies, gamemap.particles)
    GameObserver.buff_collide(gamemap.buffs, gamemap.player)
    if gamemap.player.is_dead:
        if gamemap.player.lifes > 0:
            gamemap.player.revive()
        else:    
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


    


