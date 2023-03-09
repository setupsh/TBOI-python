import os
assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
extension = '.txt'

def load_level(filename: str):
    file = open(assets_path + filename, 'r')
    return file.readlines()

levels_list = []

base_level = load_level('baselevel.txt')
level_1 = load_level('1level.txt')

for i in os.listdir(assets_path):
    levels_list.append(i)

print(levels_list)





