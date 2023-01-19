import pygame
import os
from enum import Enum


pygame.init()
assets_path = os.path.dirname(__file__) + '/assets/Sounds'

def init():
    pygame.mixer.init()

def LoadSound(filrname) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(assets_path + filrname)

class Sounds(Enum):
    Bite = 0,
    Horse = 1.

class Sound:
    BiteSound = LoadSound('/Bite.wav')
    HorseSound = LoadSound('/Horse.wav')


    def PlayOne(sound):
        match sound:
            case Sounds.Bite:
                Sound.BiteSound.play()
            case Sounds.Horse:
                Sound.HorseSound.play()

class Tracks:
    Beats = '/beats.mp3'
    MenuTheme = '/main.mp3'

class Music():
    def load_music(filename: str):
        return pygame.mixer.music.load(assets_path + filename)

    def play():
        pygame.mixer.music.play(999999)