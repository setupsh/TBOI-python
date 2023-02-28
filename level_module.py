import os

# TODO: хранить ссылки на файлы с уровнями

assets_path = os.path.dirname(__file__) + '\Assets\Levels\\'
ext = ".level"

def load_level(filename: str):
    _file = open(assets_path + filename + ext, "r")
    return _file.readlines()