from PIL import Image, ImageTk
import Tkinter as tk
import ttk

import cv2

import numpy as np

import matplotlib
matplotlib.rc("figure", facecolor="white")
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename

from interface_utilities import get_default_parameters
from interface_utilities import load_parameters
from interface_utilities import save_parameters

class Window:
    def __init__(self, master, parameters):
        self.master = master
        self.parameters = parameters
        self.entries = {}
        self.if_end_task = False

        # Configurate Menubar & Frame
        self.setup_menubar()
        self.setup_frame()

    def setup_frame(self):
        self.frame = tk.Frame(self.master, bd=0)
        self.main_group = tk.LabelFrame(self.frame, bd=2)
        self.main_group.pack(fill=tk.BOTH, expand=1)
        self.left_group = tk.LabelFrame(self.main_group, bd=0)
        self.left_group.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.right_group = tk.LabelFrame(self.main_group, bd=0)
        self.right_group.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)

    def setup_menubar(self):
        # Configurate Menubar
        start_style = ttk.Style()
        start_style.configure('St.TButton', foreground='maroon')
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Quit", command=self.master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

    def isEnd(self):
        return self.if_end_task

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

    def create_entry(self, parent, text_label, text_entry, key):
        group = tk.LabelFrame(parent, bd=2)
        group.pack(fill=tk.X, expand=0, side=tk.BOTTOM)
        L1 = tk.Label(group, text=text_label)
        L1.pack(side = tk.LEFT)
        entryText = tk.StringVar()
        E1 = tk.Entry(group, bd =2, width=30, textvariable=entryText)
        entryText.set(text_entry)
        E1.pack(side = tk.RIGHT)
        self.entries[key] = entryText

    def create_scale(self, parent, text_label, value_entry, minv, maxv, step, key):
        group = tk.LabelFrame(parent, bd=2)
        group.pack(fill=tk.X, expand=0, side=tk.BOTTOM)
        L1 = tk.Label(group, text=text_label)
        L1.pack(side = tk.LEFT)
        var = tk.DoubleVar()
        S1 = tk.Scale(group, variable=var,orient=tk.HORIZONTAL, showvalue=0, from_=minv, to=maxv,resolution=step, sliderlength=7, width=20, length=150)
        S1.pack(side = tk.RIGHT)
        var.set(value_entry)
        L1 = tk.Label(group, textvariable = var)
        L1.pack(side = tk.RIGHT)
        self.entries[key] = var

    def parametrization(self, parent):
        # Record setup
        group = tk.LabelFrame(parent, bd=2)
        group.pack(fill=tk.X, expand=0, side=tk.BOTTOM)
        self.reset_button = ttk.Button(group,
                                        text='Reset',
                                        width=17,
                                        command=self.resetParameters)
        self.reset_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.load_button = ttk.Button(group,
                                text='Load Parameters',
                                width=17,
                                command=self.loadParameters)
        self.load_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.save_button = ttk.Button(group,
                                text='Save Parameters',
                                width=17,
                                command=self.saveParameters)
        self.save_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.apply_button = ttk.Button(group,
                                text = 'Apply',
                                width = 17,
                                command=self.applyEntriesToParams)
        self.apply_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # Epsilon setup
        existing_tags = self.parameters["existing_tags"]
        self.create_entry(parent, "Existing Tags", existing_tags, "existing_tags")
        # Epsilon setup
        eps, inf, sup, steps = self.parameters["eps"], 0, 1, .001
        self.create_scale(parent, "Epsilon Coeff (approxPolyDP)", eps, inf, sup, steps, "eps")
        # Kernel setup
        kernel, inf, sup, steps = self.parameters["kernel"], 3, 9, 1
        self.create_scale(parent, "Kernel (Gaussian Canny)", kernel, inf, sup, steps, "kernel")
        # Canny Edge Sigma setup
        sigma, inf, sup, steps = self.parameters["sigma"], 0, 1, 0.001
        self.create_scale(parent, "Sigma (Gaussian Canny)", sigma, inf, sup, steps, "sigma")
        # Distance seup
        min_dist, inf, sup, steps = self.parameters["min_dist"], 0, 0.095, .001
        self.create_scale(parent, "Min. Distance", min_dist, inf, sup, steps, "min_dist")
        # Distance setup
        max_dist, inf, sup, steps = self.parameters["max_dist"], 0, 0.3, .001
        self.create_scale(parent, "Max. Distance", max_dist, inf, sup, steps, "max_dist")
        # Method setup
        min_contour_area, inf, sup, steps = self.parameters["min_contour_area"], 0, 300, 10
        self.create_scale(parent, "Min. contourArea", min_contour_area, inf, sup, steps, "min_contour_area")
        # Method setup
        max_contour_area, inf, sup, steps = self.parameters["max_contour_area"], 100, 2000, 50
        self.create_scale(parent, "Max. contourArea", max_contour_area, inf, sup, steps, "max_contour_area")
        # Method setup
        method, inf, sup, steps = self.parameters["method"], 0, 2, 1
        self.create_scale(parent, "Method (SVM, DeepNetwork, Classic)", method, inf, sup, steps, "method")
        # Record setup
        record_name = self.parameters["record_name"]
        self.create_entry(parent, "Record Name", record_name, "record_name")

    def loadParameters(self):
        filename = askopenfilename(parent=self.master)
        self.parameters.update(load_parameters(filename))
        self.applyParamsToEntries()

    def saveParameters(self):
        self.applyEntriesToParams()
        initial_name = "parameters_"+self.parameters["time"]+".json"
        filename = asksaveasfilename(parent=self.master, initialfile=initial_name)
        save_parameters(self.parameters, filename)

    def resetParameters(self):
        self.parameters.update(get_default_parameters())
        self.applyParamsToEntries()

    def applyParamsToEntries(self):
        for key in self.parameters:
            if key in self.entries:
                self.entries[key].set(self.parameters[key])
        save_parameters(self.parameters)

    def applyEntriesToParams(self):
        for key in self.entries:
            self.parameters[key] = self.entries[key].get()
        save_parameters(self.parameters)
