import os
import random
assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
extension = '.txt'

levels_list = []

def load_level(filename: str):
    file = open(assets_path + filename, 'r')
    return file.readlines()

def get_random_level():
    global levels_list
    return random.choice(levels_list)

for i in os.listdir(assets_path):
    levels_list.append(load_level(i))

print(get_random_level())






