import pygame 
clock = pygame.time.Clock()
fps = 60


class Time:
    tick: int = 0
    time_scale: float = 1
    delta_time: int = 0

    def update():
        Time.tick = clock.tick(fps)
        Time.delta_time = Time.tick * 0.001 * Time.time_scale     