# Credit for most of this to https://stackoverflow.com/a/48137257/4110625 and https://stackoverflow.com/a/48069295/4110625

import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import numpy as np
import matplotlib.pyplot as plt

from faceblur.fileloader import save_file


def _r(x):
    return int(round(x))


class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class Zoom(ttk.Frame):
    ''' Simple zoom with mouse wheel '''

    def __init__(self, mainframe, in_files, out_path):
        ''' Initialize the main Frame '''
        self.blur_mode = False
        self.center_coords = []

        self.img_idx = 0
        self.in_files = in_files
        self.out_path = out_path

        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Face Blurrrrrr')

        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # Open image

        self.image = Image.open(in_files[self.img_idx])
        # Create canvas and put image on it
        self.canvas = tk.Canvas(
            self.master,
            highlightthickness=0,
            xscrollcommand=hbar.set,
            yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        vbar.configure(
            command=self.canvas.yview)  # bind scrollbars to the canvas
        hbar.configure(command=self.canvas.xview)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<ButtonPress-1>', self.blur_or_drag)
        self.canvas.bind('<Key>', self.key)
        self.canvas.bind('<B1-Motion>', self.move_to)
        self.canvas.bind('<MouseWheel>',
                         self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',
                         self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',
                         self.wheel)  # only with Linux, wheel scroll up
        # Show image and plot some random test rectangles on the canvas
        self.imscale = .31
        self.imageid = None
        self.delta = 0.75
        self.text = self.canvas.create_text(0, 0, anchor='nw', text='')
        self.switch_img()

    def blur_or_drag(self, event):
        if self.blur_mode:
            coords = self.canvas.coords(self.text)

            x = _r((self.canvas.canvasx(event.x) - coords[0]) / self.imscale)
            y = _r((self.canvas.canvasy(event.y) - coords[1]) / self.imscale)
            self.blur(x, y)
        else:
            self.move_from(event)

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def wheel(self, event):
        # print (event.delta) # TODO: on windows the delta needs to be divided by 120
        ''' Zoom with mouse wheel '''
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if (event.num == 5 or event.delta < 0) and self.imscale > .3:
            scale *= self.delta
            self.imscale *= self.delta
        if (event.num == 4 or event.delta > 0) and self.imscale < 1.5:
            scale /= self.delta
            self.imscale /= self.delta
        # Rescale all canvas objects
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.scale('all', x, y, scale, scale)
        self.switch_img()

    def show_image(self):
        ''' Show image on the Canvas '''
        if self.imageid:
            self.canvas.delete(self.imageid)
            self.imageid = None
            self.canvas.imagetk = None  # delete previous image from the canvas
        width, height = self.image.size
        new_size = int(self.imscale * width), int(self.imscale * height)
        imagetk = ImageTk.PhotoImage(self.image.resize(new_size))
        # Use self.text object to set proper coordinates
        self.imageid = self.canvas.create_image(
            self.canvas.coords(self.text), anchor='nw', image=imagetk)
        self.canvas.lower(self.imageid)  # set it into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def key(self, event):
        """ Scrolling with the keyboard.
            Independent from the language of the keyboard, CapsLock, <Ctrl>+<key>, etc. """
        # print (event.keycode)
        if event.keycode in [100]:  # scroll right, keys 'd' or 'Right'
            if self.img_idx == len(self.in_files) - 1:
                save_file(self.in_files[self.img_idx], self.image, self.out_path)

            if self.img_idx < len(self.in_files) - 1:
                save_file(self.in_files[self.img_idx], self.image, self.out_path)

                self.img_idx += 1
                self.image = Image.open(self.in_files[self.img_idx])
                self.switch_img()
        elif event.keycode in [97]:  # scroll left, keys 'a' or 'Left'
            if self.img_idx > 0:
                self.img_idx -= 1
                self.image = Image.open(self.in_files[self.img_idx])
                self.switch_img()
        elif event.keycode in [119]:  # scroll up, keys 'w' or 'Up'
            self.blur_mode = True
            self.canvas.config(cursor='cross')
        elif event.keycode in [115]:  # scroll down, keys 's' or 'Down'
            self.image = Image.open(self.in_files[self.img_idx])
            self.switch_img()

    def switch_img(self):
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.focus_set()

    def blur(self, x, y):
        if len(self.center_coords) == 0:
            self.canvas.config(cursor='cross red red')
            self.center_coords = [x, y]
        else:
            radius = _r(
                np.linalg.norm(np.array(self.center_coords) - np.array([x, y])))
            if radius > 1:
                box = (self.center_coords[0] - radius,
                       self.center_coords[1] - radius,
                       self.center_coords[0] + radius,
                       self.center_coords[1] + radius)

                crop_img = self.image.crop(box)
                bigsize = (crop_img.size[0] * 3, crop_img.size[1] * 3)
                mask = Image.new('L', bigsize, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + bigsize, fill=255)
                mask = mask.resize(crop_img.size, Image.ANTIALIAS)
                crop_img.putalpha(mask)
                blur_image = crop_img.filter(
                    ImageFilter.GaussianBlur(radius=10))
                self.image.paste(blur_image, box, blur_image)

                self.blur_mode = False
                self.canvas.config(cursor='arrow')
                self.center_coords = []
                self.switch_img()
