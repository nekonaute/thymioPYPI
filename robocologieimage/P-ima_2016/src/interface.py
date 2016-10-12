from PIL import Image, ImageTk
import Tkinter as tk
import ttk
import cv2

from window import Window
from mainwindow import MainWindow
from startwindow import StartWindow
from controllerwindow import ControllerWindow

class Interface(object):
    def __init__(self, title, parameters):
        self.root = tk.Tk()
        ttk.Style().configure("TButton", padding=0, relief="flat",
           background="#ccc", width=5)
        #self.root.tk.call('tk', 'scaling', 1.466)
        self.root.title(title)
        self.parameters = parameters
        self.app = Window(self.root, self.parameters)
        self.root.protocol("WM_DELETE_WINDOW", self.kill)
        self.online = True
        self.title = title


    def switchState(self, state_type, *args):
        self.root.withdraw()
        self.root = tk.Toplevel(self.root)
        self.app = state_type(self.root, self.parameters, *args)
        self.online = True

    def update(self, *args):
        self.app.update(*args)
        self.root.update()
        if self.app.isEnd():
            self.online = False
        #self.root.update_idletasks()

    def isOnline(self):
        return self.online

    def getStateType(self, state_name):
        if state_name == "MainWindow":
            return MainWindow
        elif state_name == "StartWindow":
            return StartWindow
        elif state_name == "ControllerWindow":
            return ControllerWindow

    def getCurrentStateName(self):
        if isinstance(self.app, MainWindow):
            return "MainWindow"
        elif isinstance(self.app, StartWindow):
            return "StartWindow"
        elif isinstance(self.app, ControllerWindow):
            return "ControllerWindow"

    def getParameters(self):
        return self.app.parameters

    @property
    def exit(self):
        return self.online == False

    def kill(self):
        self.online = False
        #self.root.destroy()
        self.root.quit()
        cv2.destroyAllWindows()

    def isRecording(self):
        if isinstance(self.app, MainWindow):
            return self.app.if_record
        elif isinstance(self.app, StartWindow):
            return False

    def getRecordId(self):
        return self.app.parameters["record_name"]
