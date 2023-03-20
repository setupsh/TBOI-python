import os
import random
from GameObj_module import *

assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
extension = '.txt'

rooms_list = []

def load_room_from_file(filename: str):
    file = open(assets_path + filename, 'r')
    return file.readlines()

for i in os.listdir(assets_path):
    rooms_list.append(load_room_from_file(i))

class Room:
    CHAR_EMPTY = ' '
    CHAR_FULL = 'X'
    CHAR_DOOR = 'D'
    CHAR_PSYCHO = 'P'
    CHAR_CHASER = 'C'
    CHAR_SHOOTER = 'S'

    player = Player(start_pos=(scr_width * 0.5 - 24, scr_height * 0.5 - 24 ), start_size=(48,48), sprite=Sprites.player)
    
    def __init__(self, layout: list[str]) -> None:
        self.id = hash(self)
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
    def is_cleared(self) -> bool: return len(self.enemies.enemy_list) == 0

    def get_blocks_of_type(self, t: type) -> List:
        result: List[t] = list()
        for block in self.blocks:
            if type(block) == t:
                result.append(block)
        return result

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
    baseroom: Room
    rooms: dict[int, Room]
    transitions: dict[str, int] = {}

    def __init__(self, expand_iterations: int) -> None:
        self.generate(expand_iterations)

    def generate(self, expand_iterations: int):
        self.rooms = {}
        self.baseroom = Room(self._load_room(0))
        new_room = self.baseroom
        self.rooms[new_room.id] = new_room
        for door in new_room.get_blocks_of_type(Door):
            door: Door
            neighbour_room = Room(self._load_random_room())
            self.transitions[f"{new_room.id}-{door.direction}"] = neighbour_room.id
            self.transitions[f"{neighbour_room.id}-{door.alternate_direction}"] = new_room.id
            self.rooms[neighbour_room.id] = neighbour_room
        print(self.transitions)
        print(set(map(hash, self.rooms)))
        # for i in range(1, expand_iterations):
        #     self.create_room()

    def create_room(self):
        pass

    def _load_room(self, room_id: int):
        return rooms_list[room_id]
    
    def _load_random_room(self):
        return random.choice(rooms_list)

    def get_room(self, room_id: int) -> Room:
        return self.rooms.get(room_id, self.baseroom)

    def get_random_room(self) -> Room:
        return random.choice(self.rooms)

    def get_next_room(self, current_room: Room, door_direction: Direction) -> Room:
        key = f"{current_room.id}-{door_direction}"
        print(f"Try find: {key}.")
        if key in self.transitions:
           print(f"Got the key. Next level will be {self.transitions[key]}")
           return self.get_room(self.transitions[key])
        print("Gotn't key.")
        return self.baseroom