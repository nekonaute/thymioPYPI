from PIL import Image, ImageTk
import Tkinter as tk
import ttk
import cv2


from mainwindow import MainWindow
from startwindow import StartWindow

class Interface(object):
    def __init__(self, title):
        self.root = tk.Tk()
        ttk.Style().configure("TButton", padding=0, relief="flat",
           background="#ccc", width=5)
        #self.root.tk.call('tk', 'scaling', 1.466)
        self.root.title(title)
        self.app = StartWindow(self.root, title)
        self.root.protocol("WM_DELETE_WINDOW", self.kill)
        self.alive = True
        self.title = title

    def update(self, cameras=None, detectors=None, seconds=None, out=None):
        if isinstance(self.app, MainWindow):
            self.app.update(cameras, detectors, seconds, out)
            if self.app.if_end_acquisition:
                self.root.withdraw()
                self.root = tk.Toplevel(self.root)
                self.app = StartWindow(self.root, self.title, self.app.parameters)
        elif isinstance(self.app, StartWindow):
            self.app.update()
            if self.app.if_init_acquisition:
                self.root.withdraw()
                self.root = tk.Toplevel(self.root)
                self.app = MainWindow(self.root, self.title, self.app.parameters)
        self.root.update()
        #self.root.update_idletasks()

    def getState(self):
        if isinstance(self.app, MainWindow):
            return "MainWindow"
        elif isinstance(self.app, StartWindow):
            return "StartWindow"

    @property
    def exit(self):
        return self.alive == False

    def kill(self):
        self.alive = False
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
