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
        self.particles.draw()
        self.player.draw()
        self.projectiles.draw()
        self.enemies.draw()

class Level:
    baseroom: Room
    rooms: dict[int, Room]
    transitions: dict[str, int] = {} # "roomhash-direction" : next_room_hash

    def _load_room_layout(self, layout_id: int):
        return rooms_list[layout_id]
    
    def _load_random_room_layout(self):
        return random.choice(rooms_list)

    def __init__(self, expand_iterations: int) -> None:
        self.expand_iterations = expand_iterations
        self.generate()

    def generate(self):
        self.rooms = {}
        self.baseroom = Room(self._load_room_layout(0))
        self._create_node(self.baseroom)
        print(self.transitions)
        print(set(map(hash, self.rooms)))

    def _create_node(self, centre_room: Room):
        self.expand_iterations -= 1
        self.rooms[centre_room.id] = centre_room
        for door in centre_room.get_blocks_of_type(Door):
            door: Door
            neighbour_room = self._find_neighbour_room(centre_room, door)
            hub_key = f"{centre_room.id}-{door.direction}"
            neighbour_key = f"{neighbour_room.id}-{door.alternate_direction}"
            if hub_key not in self.transitions:
                self.transitions[hub_key] = neighbour_room.id
            if neighbour_key not in self.transitions:
                self.transitions[neighbour_key] = centre_room.id
            if self.expand_iterations > 0:
                self.expand_iterations -= 1
                self.rooms[neighbour_room.id] = neighbour_room
                #self._create_node(neighbour_room)

    def _find_neighbour_room(self, centre_room: Room, door_in: Door) -> Room:
        new_room: Room = Room(self._load_random_room_layout())
        has_door_out: bool = False
        for door in new_room.get_blocks_of_type(Door):
            door: Door
            if door.direction == door_in.alternate_direction:
                has_door_out = True
                break
        if not has_door_out or new_room.layout == centre_room.layout:
            new_room = self._find_neighbour_room(centre_room, door_in)
        return new_room

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
        return current_room