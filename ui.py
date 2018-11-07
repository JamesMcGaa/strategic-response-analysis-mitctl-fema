#!/usr/bin/env python 1
import Tkinter as tk 
import os
from PIL import Image, ImageTk


#from Tkinter import *

class App:
    def change_run(self, x):
        print(x)

    def __init__(self, master):
        self.frame = tk.Frame(master, background="white")
        self.frame.grid()
        self.frame.winfo_toplevel().title("Disaster Reponse Analysis")

        self.input_frame = tk.Frame(self.frame, background="grey", height = 500, width = 400)
        self.stat_image_frame = tk.Frame(self.frame, background="grey", height = 500, width = 325)
        self.dummy_frame = tk.Frame(self.frame, background="grey", height = 500, width = 325)
        self.nonfixed_frame = tk.Frame(self.frame, background="grey", height = 500, width = 325)
        self.input_frame.grid_propagate(0)
        self.dummy_frame.grid_propagate(0)
        self.stat_image_frame.grid_propagate(0)
        self.nonfixed_frame.grid_propagate(0)
        self.input_frame.grid(row=0, column=0)
        self.stat_image_frame.grid(row=0, column=1)
        self.dummy_frame.grid(row=0, column=2)
        self.nonfixed_frame.grid(row=0, column=3)


        path = "C:\\Users\\mitadm\\Documents\\urop\\outputData\\2018-11-01_16_11_26_513000_Water"

        tkimage = ImageTk.PhotoImage(Image.open(os.path.join(path, "demand_distribution.png")).resize((300,225), resample=Image.BICUBIC))
        label = tk.Label(self.stat_image_frame, image=tkimage)
        label.image = tkimage
        label.grid(row=0,  padx=10, pady=10)

        tkimage = ImageTk.PhotoImage(Image.open(os.path.join(path, "sublocation_distribution_trunc.png")).resize((300,225), resample=Image.BICUBIC))
        label = tk.Label(self.stat_image_frame, image=tkimage)
        label.image = tkimage
        label.grid(row=1,  padx=10, pady=10)



        optionList = os.listdir(os.path.join(os.getcwd(), 'outputData'))
        self.files = tk.StringVar()
        self.files.set(optionList[0])
        self.om = tk.OptionMenu(self.input_frame, self.files, *optionList, command=self.change_run)
        self.om.grid()


        for i in range(10):
            label = tk.Label(self.dummy_frame, text=str(i))
            label.grid(row=i,  padx=10, pady=0)

        most_recent = os.listdir(os.path.join(os.getcwd(), 'outputData'))[-1]


        

root = tk.Tk()
root.name = "Disaster Response"
app = App(root)
root.mainloop()


