import Tkinter as tk
import ttk
import time

from window import Window

def printf(a):
    print(a)

class StartWindow(Window):
    def __init__(self, master, title, parameters={}):
        self.master = master
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Quit", command=self.master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)
        self.title = title
        self.parameters = parameters
        self.entries = {}
        self.if_init_acquisition = False
        self.frame = tk.Frame(self.master, bd=0)
        self.main_group = tk.LabelFrame(self.frame, bd=2)
        self.main_group.pack(fill=tk.BOTH, expand=1)
        self.left_group = tk.LabelFrame(self.main_group, bd=0)
        self.left_group.pack(fill=tk.BOTH, expand=1)
        self.checkbox_record(self.entries, self.parameters)
        self.parametrization(self.left_group, self.entries, self.parameters)
        self.startButton = ttk.Button(self.frame, text='Initiate Acquisition',
                                    width=40, style='St.TButton', command=self.init_acquisition)
        self.startButton.pack(fill=tk.BOTH, expand=1)
        self.frame.pack(fill=tk.BOTH, expand=1)

    def checkbox_record(self, entries, parameters):
        check_record = tk.IntVar()
        C2 = tk.Checkbutton(self.left_group, text = "Record Video", variable = check_record, \
                         onvalue = 1, offvalue = 0, height=2, \
                         width = 20)
        check_record.set(1)
        C2.pack()
        self.entries["record"] = check_record
        self.parameters["record"] = check_record.get()

    def init_acquisition(self, *args):
        self.if_init_acquisition = True
        self.applyParams(self.entries, self.parameters)

    def update(self):
        pass
