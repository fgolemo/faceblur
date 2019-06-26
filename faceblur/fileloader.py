import os

from faceblur.data import DATA_PATH


def get_files(path=f"{DATA_PATH}/in"):
    files = [f"{path}/{x}" for x in os.listdir(path) if ".png" in x]
    return files

def save_file(in_file, img, path=f"{DATA_PATH}/out"):
    img.save(f"{path}/{os.path.basename(in_file)}")

print(get_files())
