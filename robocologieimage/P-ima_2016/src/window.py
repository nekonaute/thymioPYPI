from PIL import Image, ImageTk
import Tkinter as tk
import ttk
import json
import pickle

import cv2

import numpy as np

import matplotlib
import time
matplotlib.rc("figure", facecolor="white")
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename

class Window:
    def switch_mode(self, mode):
        self.mode = mode

    def close_windows(self):
        self.master.quit()
        self.master.destroy()
        self.alive = False

    def update_image(self, frame, channel, h, w):
        frame = cv2.resize(frame, (h, w), interpolation=cv2.INTER_AREA)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        channel.imgtk = imgtk
        channel.configure(image=imgtk)

    def add_plot(self, widget):
        f = Figure(figsize=(6, 3), dpi=100)
        f = Figure(figsize=(4, 2), dpi=50)
        a = f.add_subplot(111)#, projection='3d')
        canvas = FigureCanvasTkAgg(f, master=widget)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        return f, a

    def draw_plot(self, seconds, tag_X, tag_Y, previous_tags):
        if self.timer > seconds:
            if not self.current_tagid in previous_tags:
                self.subplot_Xpos.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], 'ro')
                self.subplot_Ypos.plot([self.timer-seconds, self.timer], [self.curr_tag_Y, tag_Y], 'ro')
                self.subplot_Xpos.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], 'r-')
                self.subplot_Ypos.plot([self.timer-seconds, self.timer], [self.curr_tag_Y, tag_Y], 'r-')
                #self.a.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], [self.curr_tag_Y, tag_Y], 'ro', linewidth=2)
                drop = True
            else:
                self.subplot_Xpos.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], 'g-')
                self.subplot_Ypos.plot([self.timer-seconds, self.timer], [self.curr_tag_Y, tag_Y], 'g-')
                #self.a.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], [self.curr_tag_Y, tag_Y], 'g-', linewidth=2)
                drop = False
            if int(self.timer) % 5 == 0:
                self.figure_Xpos.canvas.draw()
                self.figure_Ypos.canvas.draw()
            return drop
        return False

    @staticmethod
    def create_entry(parent, text_label, text_entry, key, entries):
        group = tk.LabelFrame(parent, bd=2)
        group.pack(fill=tk.X, expand=0, side=tk.BOTTOM)
        L1 = tk.Label(group, text=text_label)
        L1.pack(side = tk.LEFT)
        entryText = tk.StringVar()
        E1 = tk.Entry(group, bd =2, width=30, textvariable=entryText)
        entryText.set(text_entry)
        E1.pack(side = tk.RIGHT)
        entries[key] = entryText

    @staticmethod
    def create_scale(parent, text_label, value_entry, minv, maxv, step, key, entries):
        group = tk.LabelFrame(parent, bd=2)
        group.pack(fill=tk.X, expand=0, side=tk.BOTTOM)
        L1 = tk.Label(group, text=text_label)
        L1.pack(side = tk.LEFT)
        var = tk.DoubleVar()
        S1 = tk.Scale(group, variable=var,orient=tk.HORIZONTAL, showvalue=0, from_=minv, to=maxv,resolution=step, sliderlength=5, width=20, length=150)
        S1.pack(side = tk.RIGHT)
        var.set(value_entry)
        L1 = tk.Label(group, textvariable = var)
        L1.pack(side = tk.RIGHT)
        entries[key] = var

    def openjson(self):
        filename = askopenfilename(parent=self.master)
        with open(filename, 'r') as fp:
            data = json.load(fp)
        return data

    def loadParams(self, parameters, entries=None):
        data = self.openjson()
        for key in data:
            if isinstance(entries, dict):
                entries[key].set(data[key])
            parameters[key] = data[key]

    def saveParams(self, parameters):
        filename = asksaveasfilename(parent=self.master)
        with open(filename, 'w') as fp:
            json.dump(parameters, fp, sort_keys=True, indent=4)

    def saveAcquisition(self, data):
        filename = asksaveasfilename(parent=self.master, initialfile=self.parameters["record_name"]+".pkl")
        with open(filename, 'wb') as fp:
            pickle.dump(data, fp)

    def applyParams(self, entries, parameters):
        for key in entries:
            parameters[key] = entries[key].get()

    def parametrization(self, parent, entries, parameters):
        # Custom parameters
        start_style = ttk.Style()
        start_style.configure('St.TButton', foreground='maroon')

        # Record setup
        group = tk.LabelFrame(parent, bd=2)
        group.pack(fill=tk.X, expand=0, side=tk.BOTTOM)
        self.loadButton = ttk.Button(group, text = 'Load Parameters', width = 20, command=lambda: self.loadParams(parameters, entries))
        self.loadButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.saveButton = ttk.Button(group, text = 'Save Parameters', width = 20, command=lambda: self.saveParams(parameters))
        self.saveButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.applyButton = ttk.Button(group, text = 'Apply', width = 20, command=lambda: self.applyParams(entries, parameters))
        self.applyButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Epsilon setup
        existing_tags = parameters.get("existing_tags", '[]')
        self.create_entry(parent, "Existing Tags", existing_tags, "existing_tags", entries)

        # Epsilon setup
        eps, inf, sup, steps = parameters.get("eps", 0.100), 0, 1, .001
        self.create_scale(parent, "Epsilon Coeff (approxPolyDP)", eps, inf, sup, steps, "eps", entries)

        # Kernel setup
        kernel, inf, sup, steps = parameters.get("kernel", 3), 3, 9, 1
        self.create_scale(parent, "Kernel (Gaussian Canny)", kernel, inf, sup, steps, "kernel", entries)

        # Canny Edge Sigma setup
        sigma, inf, sup, steps = parameters.get("sigma", .10), 0, 1, 0.001
        self.create_scale(parent, "Sigma (Gaussian Canny)", sigma, inf, sup, steps, "sigma", entries)

        # Distance setup
        min_dist, inf, sup, steps = parameters.get("min_dist", 0.005), 0, 0.095, .001
        self.create_scale(parent, "Min. Distance", min_dist, inf, sup, steps, "min_dist", entries)

        # Distance setup
        max_dist, inf, sup, steps = parameters.get("max_dist", 0.095), 0, 0.3, .001
        self.create_scale(parent, "Max. Distance", max_dist, inf, sup, steps, "max_dist", entries)

        # Method setup
        min_contour_area, inf, sup, steps = parameters.get("min_contour_area", 50), 0, 300, 10
        self.create_scale(parent, "Min. contourArea", min_contour_area, inf, sup, steps, "min_contour_area", entries)

        # Method setup
        max_contour_area, inf, sup, steps = parameters.get("max_contour_area", 800), 100, 2000, 50
        self.create_scale(parent, "Max. contourArea", max_contour_area, inf, sup, steps, "max_contour_area", entries)

        # Method setup
        method, inf, sup, steps = parameters.get("method", 0), 0, 2, 1
        self.create_scale(parent, "Method (SVM, DeepNetwork, Classic)", method, inf, sup, steps, "method", entries)

        # Record setup
        record_name = parameters.get("record_name", "record_"+time.strftime("%Y%m%d-%H%M%S"))
        self.create_entry(parent, "Record Name", record_name, "record_name", entries)

        self.applyParams(entries, parameters)
