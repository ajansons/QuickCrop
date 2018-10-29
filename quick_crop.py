import os
import pathlib
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk

class QuickCrop:
    def __init__(self, master):
        self.master = master
        master.title("Quick Crop")

        self.label = Label(master, text="Select a folder to search for images.")
        self.label.pack(padx=20, pady=20)

        self.greet_button = Button(master, text="Open Folder", command=self.choose_folder)
        self.greet_button.pack(padx=20, pady=20)

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack(padx=20, pady=20)

        self.status = Label(master, text="Waiting for images…", bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

        self.padding_x = 50
        self.padding_y = 50
        self.index = 0

    def choose_folder(self):
        folder_selected = askdirectory()
        images = self.find_images(folder_selected)
        if images == []:
            messagebox.showerror("Error", "Couldn't find any images in %s" % folder_selected)
        else:
            self.images = images
            self.unpack_buttons()
            self.show_images()
            
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

    def show_images(self):
        image = Image.open(str(self.images[self.index]))
        display = ImageTk.PhotoImage(image)

        self.canvas = Canvas(self.master, width=image.width + 2*self.padding_x,
                                          height=image.height + 2*self.padding_y,
                                          cursor="cross")
        self.canvas.image = display
        self.canvas.create_image(self.padding_x, self.padding_y, image=display, anchor=NW)

        self.canvas.pack(expand=YES, fill=BOTH)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = self.start_y = None
        self.x = self.y = 0

        self.update_status_bar("image %d/%d" % (self.index + 1, len(self.images)))

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='magenta', fill="black", stipple="gray50")

    def on_move_press(self, event):
        current_x, current_y = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)

        print(self.start_x - self.padding_x,
              self.start_y - self.padding_y, 
              current_x - self.padding_x, 
              current_y - self.padding_y)

    def on_button_release(self, event):
        self.index += 1
        self.canvas.pack_forget()
        self.show_images()

    def unpack_buttons(self):
        self.label.pack_forget()
        self.greet_button.pack_forget()
        self.close_button.pack_forget()

root = Tk()
my_gui = QuickCrop(root)
root.mainloop()