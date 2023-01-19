import pygame
import os
from enum import Enum

assets_path = os.path.dirname(__file__) + '\Assets\Sprites'

def load_sprite(filename: str) -> pygame.image:
    return pygame.image.load(assets_path + filename)

class Sprites:
    player = load_sprite('\\player.png')
    enemy_circle = load_sprite('\\enemy_circle.png')    
    enemy_cube = load_sprite('\\enemy_cube.png')    
    enemy_triangle = load_sprite('\\enemy_triangle.png')
    bullet = load_sprite('\\bullet.png')
    explosion = load_sprite('\\eplosion.png')
    boss = load_sprite('\\boss.png')
    list_enemies = (enemy_circle, enemy_cube, enemy_triangle)   

class BackGrounds:
    space = load_sprite('\\ick.png')

