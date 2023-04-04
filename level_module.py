import os
import random
from GameObj_module import *
assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
extension = '.txt'

rooms_list = []

def load_level(filename: str):
    file = open(assets_path + filename, 'r')
    return file.readlines()

def get_random_level():
    global rooms_list
    return random.choice(rooms_list)

for i in os.listdir(assets_path):
    rooms_list.append(load_level(i))

class Room():
    CHAR_EMPTY = ' '
    CHAR_FULL = 'X'
    CHAR_DOOR = 'D'
    CHAR_PSYCHO = 'P'
    CHAR_CHASER = 'C'
    CHAR_SHOOTER = 'S'
    CHAR_BUFF = 'B'
    MAP = (
        
    )        

    player = Player(start_pos=(scr_width * 0.5 - 24, scr_height * 0.5 - 24 ), start_size=(48,48), sprite=Sprites.player)

    def __init__(self, layout: list[str]):
        self.id = hash(self)
        self.layout = layout
        self.blocks: List[Block] = list()
        self.floor_object: List[Block] = list()
        self.projectiles = Projectiles()
        self.particles = Particles()
        self.enemies = Enemies()
        self.buffs = Buffs()
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
                    self.enemies.add(PsychoMover((x,y), (48,48), Sprites.easy_enemy, self.player))
                elif c == self.CHAR_BUFF:
                    buff = random.choice((MedKit, RPG7, FunGhost, None))
                    if buff:
                        self.buffs.append_projectile(buff((x,y), self.player))    

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
                self.floor_object.append(Floor([x, y]))

    @property
    def is_cleared(self) -> bool: return len(self.enemies.enemy_list) == 0

    def replace_block(self, old, new):
        self.blocks.append(new)
        self.blocks.remove(old)
    def get_blocks_of_type(self, t: type):
        result:List[t] = list()
        for block in self.blocks:
            if type(block) == t:
                result.append(block)
        return result        
                

    def update(self):
        self.player.update()                
        self.projectiles.update()
        self.particles.update()
        self.enemies.update()

    def draw(self):
        for i in self.floor_object:
            i.draw()    
        for i in self.blocks:
            i.draw()
        self.player.draw()                
        self.projectiles.draw()
        self.particles.draw()
        self.enemies.draw()
        self.buffs.draw()

class Level():
    baseroom: Room
    rooms: dict[int, Room]
    transistions: dict[str, int] = {}

    def load_room_layout(self, room_id: int):
        return rooms_list[room_id]

    def load_random_room_layout(self):
        return random.choice(rooms_list)

    def __init__(self, iterartion: int):
        self.iteration = iterartion
        self.generate()

    def generate(self):
        self.rooms = {}
        self.baseroom = Room(self.load_room_layout(0))
        self.create_node(self.baseroom)
        self.expand(self.get_neighbour_rooms(self.baseroom))
        print(self.transistions)

    def expand(self, rooms: Set[Room]):
        self.iteration -= 1

        new_rooms: Set[Room] = set()
        for room in rooms:
            self.create_node(room)
            new_rooms.update(self.get_neighbour_rooms(room))

        if self.iteration > 0:
            self.expand(new_rooms)        

    def create_node(self, room: Room):
        self.rooms[room.id] = room

    def get_neighbour_rooms(self, centre_room: Room):
        neighbour_rooms: Set[Room] = set()
        for door in centre_room.get_blocks_of_type(Door):
            door: Door
            neighbour_room = self.find_neighbour_room(centre_room, door)

            hub_key = f'{centre_room.id}-{door.direction}'
            neighbour_key = f'{neighbour_room.id}-{door.alternative_direction}'

            if not hub_key in self.transistions:
                self.transistions[hub_key] = neighbour_room.id
            if not neighbour_key in self.transistions:
                self.transistions[neighbour_key] = centre_room.id
            neighbour_rooms.add(neighbour_room)
        return neighbour_rooms        

    def find_neighbour_room(self, centere_room: Room, door_in: Door):
        new_room: Room = Room(self.load_random_room_layout())
        has_door_out: bool = False
        if new_room.layout == centere_room.layout:
            new_room = self.find_neighbour_room(centere_room, door_in)
        for door in new_room.get_blocks_of_type(Door):
            door: Door
            if door.direction == door_in.alternative_direction:
                has_door_out = True
            elif self.iteration < 2:
                new_room.replace_block(door, Wall((door._pos_x, door._pos_y)))
        if not has_door_out:
            new_room = self.find_neighbour_room(centere_room, door_in)
        return new_room
        
    def get_room(self, room_id: int) -> Room:
        return self.rooms.get(room_id, self.baseroom)
    
    def get_random_room(self) -> Room:
        return random.choice(self.rooms)
    
    def get_next_room(self, current_room: Room, direction: Direction):
        key = f'{current_room.id}-{direction}'
        if key in self.transistions:
            return self.get_room(self.transistions[key])
        return current_room      








