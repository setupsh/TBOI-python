import os
assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
extension = '.txt'

def load_level(filename: str):
    file = open(assets_path + filename + extension, 'r')
    return file.readlines()

