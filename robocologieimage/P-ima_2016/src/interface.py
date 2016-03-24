from PIL import Image, ImageTk
import Tkinter as tk
import time
import cv2
import numpy as np

class Window:
    def switch_mode(self, mode):
        self.mode = mode

    def close_windows(self):
        self.master.quit()
        self.master.destroy()
        self.alive = False

    def update_image(self, frame, channel, h, w):
        frame = cv2.resize(frame, (h, w), interpolation=cv2.INTER_NEAREST)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        channel.imgtk = imgtk
        channel.configure(image=imgtk)

class MainWindow(Window):
    def __init__(self, master, title):
        self.title = title
        self.fps = 0
        self.fps_mean = 0
        self.framerate = None # label
        self.channels = {}
        self.tag_channels = {}
        self.mode = 'markers'
        self.marker_app = None
        self.master = master
        self.frame = tk.Frame(self.master)
        self.adv_button = tk.Button(self.frame, text = 'New Window', width = 25, command = self.adv_window)
        self.setup()
        #self.adv_button.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)

    def setup(self):
        self.main_group = tk.LabelFrame(self.frame)
        self.main_group.pack(fill=tk.BOTH, expand=1)
        #cameras
        self.camera_group = tk.LabelFrame(self.main_group)
        self.camera_group.pack(side=tk.LEFT,anchor=tk.NW)
        buttons_frame = tk.LabelFrame(self.camera_group)
        infos = [("original", 1), ("canny", 1), ("fgmask", 1), ("edges", 1), ("markers", 1), ("path", 1)]
        for mode, height in infos:
            tk.Button(buttons_frame, text=mode.capitalize(), command=lambda mode=mode: self.switch_mode(mode), height=height).pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        buttons_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.channel_group = tk.LabelFrame(self.camera_group)
        self.channel_group.pack(side=tk.LEFT)
        #markers
        self.tag_channel_group = tk.LabelFrame(self.main_group)
        self.tag_channel_group.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        #others
        self.information_bar = tk.LabelFrame(self.frame)
        self.information_bar.pack(fill=tk.X, expand=0)
        self.info_txt = tk.Label(self.information_bar, text='')
        self.info_txt.pack(fill=tk.X, expand=0)

    def create_channel(self, cam_id):
        r = len(self.channels) // 2
        c = len(self.channels) % 2
        self.channels[cam_id] = {}
        self.channels[cam_id]['group'] = tk.LabelFrame(self.channel_group)
        self.channels[cam_id]['group'].grid(row=r, column=c)
        self.channels[cam_id]['image'] = tk.Label(self.channels[cam_id]['group'])
        self.channels[cam_id]['image'].pack(side=tk.TOP)
        self.channels[cam_id]['descr'] = tk.Label(self.channels[cam_id]['group'], text = '', width = 25)
        self.channels[cam_id]['descr'].pack(fill=tk.X, expand=1)

    def create_tag_channel(self, marker_id):
        r = len(self.tag_channels) // 4
        c = len(self.tag_channels) % 4
        self.tag_channels[marker_id] = {}
        self.tag_channels[marker_id]['group'] = tk.LabelFrame(self.tag_channel_group)
        self.tag_channels[marker_id]['group'].grid(row=r, column=c, sticky='wens')
        self.tag_channels[marker_id]['imgroup'] = tk.LabelFrame(self.tag_channels[marker_id]['group'])
        self.tag_channels[marker_id]['imgroup'].pack(side=tk.LEFT)
        self.tag_channels[marker_id]['image'] = tk.Label(self.tag_channels[marker_id]['imgroup'])
        self.tag_channels[marker_id]['image'].pack(side=tk.TOP)
        self.tag_channels[marker_id]['ref_img'] = tk.Label(self.tag_channels[marker_id]['imgroup'])
        self.tag_channels[marker_id]['ref_img'].pack()
        self.tag_channels[marker_id]['descr'] = tk.Label(self.tag_channels[marker_id]['group'], text = '')
        self.tag_channels[marker_id]['descr'].pack(fill=tk.X, expand=1, side=tk.RIGHT)
        self.tag_channel_group.columnconfigure(c, weight=1)

    def update_fps(self, seconds):
        # Calculate frames per second
        self.fps  = 1 / seconds
        self.fps_mean = self.fps_mean + (self.fps - self.fps_mean)
        self.master.title(self.title + ' - FPS: {} (avg. {})'.format(round(self.fps, 1), round(self.fps_mean, 1)))

    def update_markers(self, detectors, seconds):
        w, h = 40, 40
        for cam_id, detector in detectors.items():
            for marker_id, marker in detector.markers_dict.items():
                if not marker_id in self.tag_channels.keys() and detector.detect_time[marker_id] > 0.5:
                    self.create_tag_channel(marker_id)
                if detector.detect_time[marker_id] > 0.5:
                    self.tag_channels[marker_id]['descr']['text'] = "Tag {}\n{},{}\n{}sec".format(str(marker_id), detector.positions[marker_id][0][0], detector.positions[marker_id][0][1], round(detector.detect_time[marker_id], 1))
                    # Update images
                    frame = detector.homothetie_markers[marker_id]
                    self.update_image(frame, self.tag_channels[marker_id]['image'], w, h)
                    # Update ref_images
                    frame = detector.refs[0][marker_id]*255
                    self.update_image(frame, self.tag_channels[marker_id]['ref_img'], w, h)

    def update_cameras(self, cameras, detectors, seconds):
        for cam_id, cam in cameras.items():
            detector = detectors[cam_id]
            if not cam_id in self.channels.keys():
                self.create_channel(cam_id)
            # Update texts
            self.channels[cam_id]['descr']['text'] = 'cam {} {} {} tags {}'.format(str(cam_id)[-8:-1], " "*10, detector.nb_tags, detector.detected)
            # Update images
            frame = detectors[cam_id].get(self.mode).copy()
            w, h = frame.shape[:2]
            w, h = max(w-w*70/100, 200), max(h-h*70/100, 300)
            self.update_image(frame, self.channels[cam_id]['image'], h, w)

    def update(self, cameras, detectors, seconds):
        self.update_fps(seconds)
        self.update_markers(detectors, seconds)
        self.update_cameras(cameras, detectors, seconds)
        self.info_txt['text'] = "{} active, {} (mode {}) \n".format(len(cameras), len(set([marker_id for detector in detectors.values() for marker_id in detector.markers_dict.keys()])), self.mode)
        #for cam_id, detector in detectors.items():
        #    self.info_txt['text'] += cam_id[-10:-1]+ " ::: {} ({}) ::: {} ({})".format(int(detector.method1), round(100*(detector.method1-detector.method1_error)/detector.method1, 2), int(detector.method2), round(100*(detector.method2-detector.method2_error)/detector.method2, 2))

    def adv_window(self):
        self.advWindow = tk.Toplevel(self.master)
        self.marker_app = AdvancedWindow(self.advWindow, self)

class AdvancedWindow(Window):
    def __init__(self, master, main):
        self.main = main
        self.master = master
        self.frame = tk.Frame(self.master)
        self.setup()
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
        self.alive = True
        self.mode = self.main.mode
        self.channels = {}

class Interface(object):
    def __init__(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.app = MainWindow(self.root, title)

    def update(self, cameras, detectors, seconds):
        self.app.update(cameras, detectors, seconds)
        self.root.update()
        self.root.update_idletasks()

    @property
    def exit(self):
        return False

    def kill(self):
        cv2.destroyAllWindows()
