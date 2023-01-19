from random import randint
#if player._pos_x >= food._pos_x and player._pos_x < food._pos_x + food._size_x and player._pos_y >= food._pos_y and player._pos_y < food._pos_y + food._size_y

white = (255, 255, 255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)


def GetColor(r: int, g:int, b:int) -> tuple[int,int,int]:
    return(r, g, b)

def RandomColor():
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return(r,g,b)


