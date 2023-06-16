from abc import ABC, abstractmethod
from cmath import rect
from typing import Tuple, List
import colorlib as Color
import pygame
from screen_module import screen 
from enum import Enum
from events_module import *

class VerticalAlignment(Enum):
    Top = 0,
    Center = 1,
    Bottom = 2
class HorizontalAlignment(Enum):
    Left = 0,
    Center = 1,
    Right = 2

class GuiComponent(ABC):
    init_x: int = 0
    init_y: int = 0

    def __init__(self, position: Tuple[int, int], horizontal : HorizontalAlignment = HorizontalAlignment.Center, vertical: VerticalAlignment = VerticalAlignment.Center) -> None:
        self.set_position(position[0], position[1], override_init=True)
        self.set_alignment(horizontal, vertical)

    def set_position(self, x, y, override_init: bool = False):
        self.position_x = x
        self.position_y = y
        if override_init:
            self.init_x = x
            self.init_y = y

    def set_alignment(self, horizontal : HorizontalAlignment, vertical: VerticalAlignment):
        self.horizontal_aligh = horizontal
        self.vertical_aligh = vertical
    def aligh(self, component_width: int, component_height: int):
        self.set_position(self.init_x,self.init_y)
        match self.horizontal_aligh:
            case HorizontalAlignment.Left:
                self.set_position(self.position_x, self.position_y)
            case HorizontalAlignment.Center:
                self.set_position(self.position_x - component_width/2, self.position_y)
            case HorizontalAlignment.Right:
                self.set_position(self.position_x - component_width, self.position_y)
        match self.vertical_aligh:
            case VerticalAlignment.Top:
                self.set_position(self.position_x, self.position_y)
            case VerticalAlignment.Center:
                self.set_position(self.position_x, self.position_y - component_height/2)
            case VerticalAlignment.Bottom:
                self.set_position(self.position_x , self.position_y - component_height)

                

    def update(self):
        pass
    @abstractmethod
    def draw(self):
        pass

class GuiLabel(GuiComponent):
    color = Color.white
    text = str('')
    def __init__(self, position: Tuple[int, int], text: str, color, font_name: str = 'Cantarell Extra Bold', font_size: int = 50, horizontal : HorizontalAlignment = HorizontalAlignment.Center, vertical: VerticalAlignment = VerticalAlignment.Center) -> None:
        super().__init__(position, horizontal, vertical)
        self.set_font(font_name, font_size)
        self.set_color(color)
        self.set_label(text)


    def set_font(self, name: str, size: int):
        self.font = pygame.font.SysFont(name, size)


    def set_color(self, color):
        self.color = color

    def set_label(self, text: str):
        self.text = text
        self.label = self.font.render(self.text, True, self.color)
        self.fit()
    def fit(self):
        self.aligh(self.label.get_width(), self.label.get_height())

    def draw(self):
        screen.blit(self.label, (self.position_x, self.position_y))

class Canvas():
    def __init__(self) -> None:
        self.GUIElements: List[GuiComponent] = []

    def append_el(self, element: GuiComponent):
        self.GUIElements.append(element)
    def extend_el(self, elements: set[GuiComponent]):
        self.GUIElements.extend(elements)
    def clear_el(self):
        self.GUIElements.clear()
    def draw(self):
        for i in self.GUIElements:
            i.draw()
    def update(self):
        for i in self.GUIElements:
            i.update()                          
class obvodka(GuiComponent):

    width = 0
    height = 0
    color = Color.black

    def __init__(self, position: Tuple[int, int], width: int, height: int, color = Color.black, horizontal: HorizontalAlignment = HorizontalAlignment.Center, vertical: VerticalAlignment = VerticalAlignment.Center) -> None:
        super().__init__(position, horizontal, vertical)
        self.set_color(color)
        self.set_size(width, height)

    def set_size(self, width , height):
        self.width = width
        self.height = height
        self.fit()

    def set_color(self, color):
        self.color = color

    def fit(self):
        self.aligh(self.width, self.height)
    rect: pygame.Rect = None
    def draw(self):
        self.rect = pygame.draw.rect(screen, self.color, (self.position_x, self.position_y, self.width, self.height))   

class Button(GuiComponent):
    defualtbgcolor = Color.white
    onpressbgcolor = Color.red
    on_press_method = None
    def __init__(self, position: Tuple[int, int], background: obvodka, caption: GuiLabel, on_press, horizontal: HorizontalAlignment = HorizontalAlignment.Center, vertical: VerticalAlignment = VerticalAlignment.Center) -> None:
        super().__init__(position, horizontal, vertical)
        self.set_button(background, caption, on_press)
    def set_button(self, bg_rect: obvodka, caption: GuiLabel, on_press):
        self.on_press_method = on_press
        self.set_bg(bg_rect)
        self.set_caption(caption)
        self.fit()
    def set_bg(self, bg_rect: obvodka):
        bg_rect.set_position(bg_rect.init_x + self. position_x, bg_rect.init_y + self.position_y, override_init=True)    
        self.background = bg_rect
    def set_caption(self, label: GuiLabel):
        label.set_position(label.init_x + self. position_x, label.init_y + self.position_y, override_init=True)    
        self.caption = label
    def fit(self):
        self.background.fit()
        self.caption.fit()
    def draw(self):
        self.background.draw()
        self.caption.draw()
    def press(self):
        self.on_press_method()
    def select(self):
        self.background.set_color(Color.green)
    def deselect(self):
        self.background.set_color(Color.black)
    def highlight(self):
        self.background.set_color(Color.green)       
    @property
    def get_mouse_pos(self): return pygame.mouse.get_pos()

    def mosue_check_colission(self):  
        return (self.get_mouse_pos[0] >= self.position_x - self.background.width * 0.5) and (self.get_mouse_pos[0] < self.position_x + self.background.width * 0.5) and (self.get_mouse_pos[1] < self.position_y + self.background.height * 0.5) and (self.get_mouse_pos[1] >= self.position_y - self.background.height * 0.5)
    def update(self):
        if self.mosue_check_colission() and Inpunting.is_mouse_pressed:
            self.press()
        if self.mosue_check_colission():
            self.highlight()
        else:
            self.deselect()        