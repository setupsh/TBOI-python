import pygame
from time_module import Time

class Sequences:
    Idle = 'idle'
    Walk = 'walk'
    Attack = 'attack'

class Animator:
    def __init__(self, idle_sequence: tuple[pygame.Surface], walk_sequence: tuple[pygame.Surface], attack_sequence: tuple[pygame.Surface], speed: float = 1) -> None:
        self.sequences={
            Sequences.Idle: idle_sequence,
            Sequences.Walk: walk_sequence,
            Sequences.Attack: attack_sequence    
        }
        self.set_animation(Sequences.Idle)
        self.set_speed(speed)


    def set_animation(self, name: str):
        self.current_sequence = self.sequences[name]
        self.current_frame = 0
        self.timer = 0

    def set_speed(self, speed: float):
        self.update_time = 0.1 / speed

    def get_updated_frame(self) -> pygame.Surface:
        return self.current_sequence[self.current_frame]
    
    def update(self) -> bool:
        self.timer -= Time.delta_time
        if self.timer <= 0:
            self.timer = self.update_time
            if self.current_frame >= len(self.current_sequence) - 1:
                self.current_frame = 0
            else:
                self.current_frame += 1
            return True        
        return False    

