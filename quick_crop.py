# -*- coding: utf-8 -*-
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
        self.max_width = 1280
        self.max_height = 720

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
        self.canvas = Canvas(self.master, width=self.max_width + 2*self.padding_x,
                                          height=self.max_height + 2*self.padding_y,
                                          cursor="cross")
        image = Image.open(str(self.images[self.index]))
        self.should_resize = image.width > self.max_width or image.height > self.max_height

        if self.should_resize:
            max_dim = self.max_width if image.width > image.height else self.max_height
            dim_to_scale = image.width if image.width > image.height else image.height
            self.scale_factor = max_dim/dim_to_scale
            self.upscale_factor = dim_to_scale/max_dim
            self.original_image = image
            self.canvas.image = image.resize((int(image.width * self.scale_factor), int(image.height * self.scale_factor)))
        else:
            self.canvas.image = image

        display = ImageTk.PhotoImage(self.canvas.image)
        # We need to have a reference to display so it doesn't get garbage collected
        self.canvas.display = display
        self.canvas.create_image(self.padding_x, self.padding_y, image=display, anchor=NW)

        self.canvas.pack(expand=YES, fill=BOTH)

        # Left mouse - ready for crop
        self.canvas.bind("<ButtonPress-1>", self.on_left_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_mouse_release)

        # Right mouse - delete and move on
        self.canvas.bind("<ButtonPress-3>", self.on_right_mouse_press)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_mouse_release)

        # Spacebar - do nothing and pass
        self.canvas.bind_all("<space>", self.next_image)

        self.rect = None
        self.start_x = self.start_y = None
        self.x = self.y = 0
        # Index of the image on the status bar has +1
        self.user_input = Entry(self.status, bg='#d6e8ee', textvariable=StringVar(self.status,self.index+1))
        self.user_input.pack(side="left")

        file_name = self.images[self.index]
        img_label = os.path.splitext(file_name)[0]

        static_status = '/' + str(len(self.images)) + ", path/label: " + img_label
        self.status_label = Label(self.status, text=static_status)
        self.status_label.place(relx=0.10, relwidth=0.65)


    def next_image(self, event=None):
        # Get user input to jump to the next image
        user_index = int(self.user_input.get())

        if user_index==self.index+1:
            self.index += 1
        else:
            # If user wants 10th image, it is actually 9th image from 0
            self.index = user_index-1
        self.canvas.pack_forget()
        self.user_input.pack_forget()
        self.status_label.pack_forget()
        if self.index < len(self.images):
            self.show_images()
        else:
            self.update_status_bar("All done!")

    # Left mouse stuff
    def on_left_mouse_press(self, event):
        # Save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='magenta', fill="black", stipple="gray50")

    def on_left_drag(self, event):
        current_x, current_y = (event.x, event.y)

        # Expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)

        self.crop_rectangle = (self.start_x - self.padding_x,
              self.start_y - self.padding_y, 
              current_x - self.padding_x, 
              current_y - self.padding_y)

    def on_left_mouse_release(self, event):

        print(self.index, self.crop_rectangle)

        self.crop_rectangle = (
            self.snap_x(self.crop_rectangle[0]),
            self.snap_y(self.crop_rectangle[1]),
            self.snap_x(self.crop_rectangle[2]),
            self.snap_y(self.crop_rectangle[3])
        )

        no_area = self.crop_rectangle[0] == self.crop_rectangle[2] or self.crop_rectangle[1] == self.crop_rectangle[3]

        print(self.index, self.crop_rectangle)

        if not no_area:
            if self.should_resize:
              self.crop_rectangle = (
              self.crop_rectangle[0] * self.upscale_factor,
              self.crop_rectangle[1] * self.upscale_factor,
              self.crop_rectangle[2] * self.upscale_factor,
              self.crop_rectangle[3] * self.upscale_factor, 
              )
              self.canvas.image = self.original_image

            cropped_file_name = self.images[self.index]
            cropped_image = self.canvas.image.crop(self.crop_rectangle).save(str(cropped_file_name))

        self.next_image()

    # Right mouse, delete the current image
    def on_right_mouse_press(self, event):
        os.remove((str(self.images[self.index])))
        self.next_image()
    
    def on_right_mouse_release(self, event):
        pass

    def unpack_buttons(self):
        self.label.pack_forget()
        self.greet_button.pack_forget()
        self.close_button.pack_forget()

    def snap_x(self, x):
        if x < 0:
            return 0
        elif x > self.canvas.image.width:
            return self.canvas.image.width
        else:
            return x

    def snap_y(self, y):
        if y < 0:
            return 0
        elif y > self.canvas.image.height:
            return self.canvas.image.height
        else:
            return y

root = Tk()
my_gui = QuickCrop(root)
root.mainloop()