import os
import pathlib
from tkinter import Tk, Label, Button
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk

class QuickCrop:
    def __init__(self, master):
        self.master = master
        master.geometry('400x400')
        master.title("Quick Crop")

        self.label = Label(master, text="Select a folder to search for images.")
        self.label.pack()

        self.greet_button = Button(master, text="Open Folder", command=self.choose_folder)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def choose_folder(self):
        folder_selected = askdirectory()
        images = self.find_images(folder_selected)
        print(images)

    def find_images(self, folder_path):
        images = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".jpg"):
                    image_file = pathlib.PurePath(root, file)
                    images.append(image_file)
        return images

root = Tk()
my_gui = QuickCrop(root)
root.mainloop()