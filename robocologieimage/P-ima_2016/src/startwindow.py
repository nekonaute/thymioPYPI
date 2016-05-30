 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import Tkinter as tk
import tkMessageBox
import ttk
import time
import os.path

from window import Window

from tkFileDialog import askopenfilename

DEFAULT_FILENAME = "default_params.json"

class StartWindow(Window):
    def __init__(self, master, parameters):
        Window.__init__(self, master, parameters)
        self.create_checkboxes(self.entries, self.parameters)
        self.parametrization(self.main_group)
        self.correctFileConsistance(self.parameters)
        self.startButton = ttk.Button(self.frame,
                                        text='Initiate Acquisition',
                                        width=40,
                                        style='St.TButton',
                                        command=self.init_acquisition)
        self.startButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.frame.pack(fill=tk.BOTH, expand=1)

    def create_checkboxes(self, entries, parameters):
        group = tk.LabelFrame(self.main_group, bd=2)
        group.pack(fill=tk.X, expand=0)
        label = tk.Label(group, text="Video Stream List (up to 4 streams)")
        label.pack(fill=tk.X, expand=1)
        self.capture_group = tk.LabelFrame(group, bd=2)
        self.capture_group.pack(fill=tk.X, expand=1)
        self.capture_label = tk.Label(self.capture_group, text="Sources:")
        self.capture_label.pack(side = tk.LEFT)
        group = tk.LabelFrame(group, bd=2)
        group.pack(fill=tk.X, expand=0)
        self.capture_entry = tk.StringVar()
        E1 = tk.Entry(group, bd =2, width=30, textvariable=self.capture_entry)
        E1.pack(side = tk.LEFT)
        saveButton = ttk.Button(group, text = 'Add Camera ID', width = 20, command=lambda: self.addCameraID(parameters))
        saveButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        tk.Label(group, text="or").pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        applyEntriesToParamsButton = ttk.Button(group, text = 'Add Video File', width = 20, command=lambda: self.addVideoFile(parameters))
        applyEntriesToParamsButton.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        record_var = tk.IntVar()
        checkbtn = tk.Checkbutton(self.frame,
                            text = "Record Video",
                            variable = record_var,
                            onvalue = 1, offvalue = 0,
                            height=1, width = 10)
        record_var.set(1)
        checkbtn.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        entries["record"] = record_var
        parameters["record"] = record_var.get()

    def addCameraID(self, parameters):
        if not 'captures' in self.parameters:
            self.parameters['captures'] = []
        entry = self.capture_entry.get()
        try:
            int_entry = int(entry)
        except ValueError:
            if self.isValidVideoFile(entry):
                if not entry in self.parameters['captures']:
                    self.parameters['captures'].append(entry)
        else:
            if not int_entry in self.parameters['captures']:
                self.parameters['captures'].append(int_entry)

    def addVideoFile(self, parameters):
        filename = askopenfilename(parent=self.master)
        if not 'captures' in self.parameters:
            self.parameters['captures'] = []
        if self.isValidVideoFile(filename):
            if not filename in self.parameters['captures']:
                self.parameters['captures'].append(filename)

    def isValidVideoFile(self, filename):
        if os.path.isfile(filename):
            if filename and (filename[-4:].lower() in ('.avi', '.mp4', '.mkv', '.mov') or filename[-5:].lower() in ('.webm')):
                return True
            else:
                try:
                    tkMessageBox.showinfo("Error", "File '{}' isn't a video (.webm, .avi, .mp4, .mkv, .mov).".format(filename))
                except UnicodeEncodeError:
                    tkMessageBox.showinfo("Error", "File isn't a video (.webm, .avi, .mp4, .mkv, .mov).".format(filename))
                return False
        else:
            try:
                tkMessageBox.showinfo("Error", "File '{}' not found.".format(filename))
            except UnicodeEncodeError:
                tkMessageBox.showinfo("Error", "File not found.".format(filename))
            return False

    def correctFileConsistance(self, parameters):
        for filename in self.parameters['captures']:
            if isinstance(filename, str):
                if not self.isValidVideoFile(filename):
                    self.parameters['captures'].remove(filename)

    def init_acquisition(self, *args):
        if not('captures' in self.parameters and self.parameters['captures']):
            tkMessageBox.showinfo("Error", "You must add camera(s) or video(s) for acquisition to proceed.")
        else:
            self.if_end_task = True
            self.next_state = "MainWindow"
            self.applyEntriesToParams()

    def update(self):
        self.capture_label['text'] = ""
        capture_list = self.parameters.get('captures', [])
        for i, capture in enumerate(capture_list):
            if i > 0:
                self.capture_label['text'] += "\n"
            self.capture_label['text'] += str(capture) + ";"
