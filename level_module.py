import os
import random
from GameObj_module import *

assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
extension = '.txt'

levels_list = []

def load_level(filename: str):
    file = open(assets_path + filename, 'r')
    return file.readlines()

def get_random_level():
    global levels_list
    return random.choice(levels_list)

for i in os.listdir(assets_path):
    levels_list.append(load_level(i))

class Room:
    CHAR_EMPTY = ' '
    CHAR_FULL = 'X'
    CHAR_DOOR = 'D'
    CHAR_PSYCHO = 'P'
    CHAR_CHASER = 'C'
    CHAR_SHOOTER = 'S'

    player = Player(start_pos=(scr_width * 0.5 - 24, scr_height * 0.5 - 24 ), start_size=(48,48), sprite=Sprites.player)
    
    def __init__(self, layout: list[str]) -> None:
        self.layout = layout
        self.blocks: List[Block] = list()
        self.floor: List[Block] = list()
        self.projectiles = Projectiles()
        self.particles = Particles()
        self.enemies = Enemies()
        self.generate()

    def generate(self):
        for i, e in enumerate(self.layout):
            for j, c in enumerate(e):
                x = j * Block._size_x
                y = i * Block._size_y
                if c == self.CHAR_FULL:
                    self.blocks.append(Wall([x, y]))
                elif c == self.CHAR_SHOOTER:
                    self.enemies.add(Shooter((x, y), (48,48), Sprites.normal_enemy, self.player, self.projectiles))
                elif c == self.CHAR_CHASER:
                    self.enemies.add(Chaser((x, y), (48,48), Sprites.hard_enemy, self.player))
                elif c == self.CHAR_PSYCHO:
                    self.enemies.add(PsychoMover((x,y), (48,48), Sprites.easy_enemy))
                elif c == self.CHAR_DOOR:
                    start_dir: Direction
                    if i == 0:
                        start_dir = Direction.Up
                    elif i == self.layout.__len__() - 1:
                        start_dir = Direction.Down 
                    elif j == 0:
                        start_dir = Direction.Left
                    elif j == self.layout[i].__len__() - 2:
                        start_dir = Direction.Right  
                    self.blocks.append(Door([x,y], start_dir))         
                self.floor.append(Floor([x, y]))

    @property
    def is_cleared(self):
        return len(self.enemies.enemy_list) == 0

    def update(self):
        self.player.update()
        self.particles.update()
        self.projectiles.update()                                               
        self.enemies.update()

    def draw(self):
        for i in self.floor:
            i.draw()
        for i in self.blocks:
            i.draw()
        self.player.draw()
        self.particles.draw()
        self.projectiles.draw()
        self.enemies.draw()

class Level:
    def __init__(self) -> None:
        pass

    def generate(self):
        pass