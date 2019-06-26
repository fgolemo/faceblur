from faceblur.fileloader import get_files
from faceblur.tk import Zoom
import tkinter as tk
from faceblur.data import DATA_PATH


def main():
    root = tk.Tk()
    app = Zoom(root, in_files=get_files(), out_path=f"{DATA_PATH}/out")
    # You can set the geometry attribute to change the root windows size
    root.geometry("1200x768")
    root.mainloop()


if __name__ == '__main__':
    main(
    )  # you can also run this with the command line script "blurp" if you installed it with "pip install -e ."
