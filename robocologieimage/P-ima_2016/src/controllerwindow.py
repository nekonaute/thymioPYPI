import Tkinter as tk
import ttk
import time

from window import Window

def printf(a):
    print(a)

class ControllerWindow(Window):
    def __init__(self, master):
        Window.__init__(self, master)
        self.captures = ["LOL"]
        self.create_entries()
        self.frame.pack(fill=tk.BOTH, expand=1)

    def create_entries(self):
        label = tk.Label(self.left_group, text="Identifiants")
        label.pack()
        group = tk.LabelFrame(self.left_group, bd=2)
        group.pack(fill=tk.X, expand=0)
        for capture in self.captures:
            label = tk.Label(group, text=str(capture))
            label.pack(side = tk.BOTTOM)
        addVideoBtn = ttk.Button(self.frame,
                                    text='Add Video',
                                    width=15,
                                    style='St.TButton',
                                    command=self.init_acquisition)
        addVideoBtn.pack(fill=tk.BOTH, expand=1)
        addCameraBtn = ttk.Button(self.frame,
                                    text='Add Camera',
                                    width=15,
                                    style='St.TButton',
                                    command=self.init_acquisition)
        addCameraBtn.pack(fill=tk.BOTH, expand=1)

    def init_acquisition(self, *args):
        self.if_init_acquisition = True
        self.applyEntriesToParams(self.entries, self.parameters)

    def update(self):
        pass
