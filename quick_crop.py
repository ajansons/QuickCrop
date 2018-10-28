import os
import pathlib
from tkinter import *
from tkinter import messagebox
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

        self.status = Label(master, text="Waiting for images…", bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

    def choose_folder(self):
        folder_selected = askdirectory()
        images = self.find_images(folder_selected)
        if images == []:
            messagebox.showerror("Error", "Couldn't find any images in %s" % folder_selected)
        else:
            self.images = images
            self.update_status_bar("Found %d images" % len(self.images))

    def find_images(self, folder_path):
        images = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".jpg"):
                    image_file = pathlib.PurePath(root, file)
                    images.append(image_file)
        return images

    def update_status_bar(self, text):
        self.status["text"] = text

root = Tk()
my_gui = QuickCrop(root)
root.mainloop()