import pygame
import os
from enum import Enum

assets_path = os.path.dirname(__file__) + '\Assets\Sprites'

def load_sprite(filename: str) -> pygame.image:
    return pygame.image.load(assets_path + filename)

class Sprites:
    player = load_sprite('\\player.png')
    easy_enemy = load_sprite('\\easy_enemy.png')    
    normal_enemy = load_sprite('\\normal_enemy.png')    
    hard_enemy = load_sprite('\\hard_enemy.png')
    block = load_sprite('\\block.png')  
    floor = load_sprite('\\floor.png')
    bullet = load_sprite('\\bullet.png')
    death_skull = load_sprite('\\dead.png')
class BackGrounds:
    pass