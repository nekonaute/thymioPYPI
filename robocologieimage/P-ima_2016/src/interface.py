from PIL import Image, ImageTk
import Tkinter as tk
import ttk
import time
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

class MainWindow(Window):
    def __init__(self, master, title):
        self.title = title
        self.fps = 0
        self.fps_mean = 0
        self.total_drops = 0
        self.total_quads = 0
        self.total_tags_selected = 0
        self.total_tags_all = 0
        self.total_success = 0
        self.total_error = 0
        self.total_doublon = 0
        self.prev_dropsPerTag = 0
        self.prev_tagPerQuads = 1
        self.curr_tag_drop = 0
        self.timer = 0
        self.loop_i = 0
        self.framerate = None # label
        self.channels = {}
        self.tag_channels = {}
        self.mode = 'markers'
        self.marker_app = None
        self.current_tagid = None
        self.curr_tag_X = None
        self.curr_tag_Y = None
        self.master = master
        self.frame = tk.Frame(self.master, bd=0)
        self.tag_app = None
        donothing = lambda x: x
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=donothing)
        filemenu.add_command(label="Open", command=donothing)
        filemenu.add_command(label="Save", command=donothing)
        filemenu.add_command(label="Save as...", command=donothing)
        filemenu.add_command(label="Close", command=donothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=donothing)

        editmenu.add_separator()

        editmenu.add_command(label="Cut", command=donothing)
        editmenu.add_command(label="Copy", command=donothing)
        editmenu.add_command(label="Paste", command=donothing)
        editmenu.add_command(label="Delete", command=donothing)
        editmenu.add_command(label="Select All", command=donothing)

        menubar.add_cascade(label="Edit", menu=editmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=donothing)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.master.config(menu=menubar)
        self.adv_button = ttk.Button(self.frame, text = 'New Window', width = 25, command = self.tag_window)
        self.setup()
        #self.adv_button.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)

    def setup(self):
        self.main_group = tk.LabelFrame(self.frame, bd=2)
        self.main_group.pack(fill=tk.BOTH, expand=1)
        self.left_group = tk.LabelFrame(self.main_group, bd=0)
        self.left_group.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.right_group = tk.LabelFrame(self.main_group, bd=0)
        self.right_group.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)
        #cameras
        self.camera_group = tk.LabelFrame(self.left_group, bd=0, bg="white")
        self.camera_group.pack(side=tk.LEFT,anchor=tk.NW,expand=1,fill=tk.X)
        buttons_frame = tk.LabelFrame(self.camera_group, bd=0)
        infos = [("original", 1), ("canny", 1), ("edges", 1), ("markers", 1), ("path", 1)]
        for mode, height in infos:
            ttk.Button(buttons_frame, text=mode.capitalize(), command=lambda mode=mode: self.switch_mode(mode)).pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        buttons_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.channel_group = tk.LabelFrame(self.camera_group, bd=0)
        self.channel_group.pack(side=tk.LEFT)
        #markers
        self.tag_channel_group = tk.LabelFrame(self.right_group, bd=0)
        self.tag_channel_group.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # Plots
        # Add plot
        self.adv_group = tk.LabelFrame(self.right_group, bd=1, bg="white")
        self.adv_group.pack(fill=tk.BOTH, expand=1, side=tk.BOTTOM)
        #descr = tk.Label(self.adv_group, text='Advanced Tag Information', bd=0)
        #descr.pack()
        # Marker focus
        self.tag_focus_group = tk.LabelFrame(self.adv_group, bd=1, bg="white")
        self.tag_focus_group.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        ## create a label in the frame
        self.tag_focus_descr = tk.Label(self.adv_group, text='Tag N/A (X time; Y: the position x of the robot in the image)', bg="white")
        self.tag_focus_descr.pack()
        self.figure_Xpos, self.subplot_Xpos = self.add_plot(self.adv_group)
        self.figure_Ypos, self.subplot_Ypos = self.add_plot(self.adv_group)
        self.tag_focus_legend = tk.Label(self.adv_group, bg="white", bd=1)
        self.tag_focus_legend.pack(fill=tk.BOTH)
        self.legend = tk.Label(self.frame)
        self.legend.pack()
        #others
        self.information_bar = tk.LabelFrame(self.frame, bd=1)
        self.information_bar.pack(fill=tk.X, expand=0)
        self.info_txt = tk.Label(self.information_bar, text='', bd=1)
        self.info_txt.pack(fill=tk.X, expand=0)

    def create_channel(self, cam_id):
        r = len(self.channels) // 2
        c = len(self.channels) % 2
        self.channels[cam_id] = {}
        self.channels[cam_id]['group'] = tk.LabelFrame(self.channel_group, bd=0)
        self.channels[cam_id]['group'].grid(row=r, column=c)
        self.channels[cam_id]['image'] = tk.Label(self.channels[cam_id]['group'])
        self.channels[cam_id]['image'].pack(side=tk.TOP)
        self.channels[cam_id]['descr'] = tk.Label(self.channels[cam_id]['group'], text = '', width = 25, bg="gray90")
        self.channels[cam_id]['descr'].pack(fill=tk.X, expand=1)

    def create_tag_channel(self, marker_id):
        r = len(self.tag_channels) // 4
        c = len(self.tag_channels) % 4
        self.tag_channels[marker_id] = {}
        self.tag_channels[marker_id]['group'] = tk.LabelFrame(self.tag_channel_group, bd=1)
        self.tag_channels[marker_id]['group'].grid(row=r, column=c, sticky='wens')
        self.tag_channels[marker_id]['imgroup'] = tk.LabelFrame(self.tag_channels[marker_id]['group'])
        self.tag_channels[marker_id]['imgroup'].pack(side=tk.LEFT)
        self.tag_channels[marker_id]['image'] = tk.Label(self.tag_channels[marker_id]['imgroup'])
        self.tag_channels[marker_id]['image'].pack(side=tk.TOP)
        self.tag_channels[marker_id]['ref_img'] = tk.Label(self.tag_channels[marker_id]['imgroup'])
        self.tag_channels[marker_id]['ref_img'].pack()
        self.tag_channels[marker_id]['descr'] = tk.Label(self.tag_channels[marker_id]['group'], text = '')
        self.tag_channels[marker_id]['descr'].pack(fill=tk.X, expand=1)
        self.tag_channels[marker_id]['tag_btn'] = ttk.Button(self.tag_channels[marker_id]['group'], text = 'Select', command = lambda: self.select_tag(marker_id))
        self.tag_channels[marker_id]['tag_btn'].pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        self.tag_channel_group.columnconfigure(c, weight=1)

    def select_tag(self, marker_id):
        self.current_tagid = marker_id
        self.tag_focus_descr['text'] = 'Tag {} (X time; Y: the position x of the robot in the image)'.format(marker_id)
        self.curr_tag_drop = 0

    def update_fps(self, seconds):
        # Calculate frames per second
        self.loop_i += 1
        self.timer += seconds
        self.fps  = 1 / seconds
        if self.loop_i > 5 and not self.fps > 45:
            self.fps_mean = self.fps_mean + (self.fps - self.fps_mean)/self.loop_i
        self.master.title(self.title + ' - FPS: {} (avg. {})'.format(min(60,round(self.fps, 1)), min(60,round(self.fps_mean, 1))))

    def update_markers(self, detectors, seconds):
        w, h = 30,30
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
            if not detector.online:
                continue
            if not cam_id in self.channels.keys():
                self.create_channel(cam_id)
            # Update texts
            self.channels[cam_id]['descr']['text'] = 'cam {} {} {} tags {}'.format(str(cam_id)[-8:-1], " "*10, int(detector.nb_selected), detector.detected)
            # Update images
            frame = detectors[cam_id].get(self.mode).copy()
            w, h = frame.shape[:2]
            w, h = max(w-w*65/100, 200), max(h-h*65/100, 300)
            self.update_image(frame, self.channels[cam_id]['image'], h, w)

    def update_info(self, cameras, detectors, seconds):
        # Compute data
        drops = .0
        nb_selected = 1e-6
        nb_detected = 1e-6
        nb_quads = 1e-6
        nb_success = 1e-6
        nb_error = 1e-6
        nb_doublon = 1e-6
        for cam_id, cam in cameras.items():
            detector = detectors[cam_id]
            if not detector.online:
                continue
            for marker_id, marker in detector.markers_dict.items():
                if not marker_id in detector.previous_tags:
                    drops += 1.
            nb_quads += detector.nb_quads
            nb_detected += detector.nb_detected
            nb_selected += detector.nb_selected
            nb_success += detector.nb_success
            nb_error += detector.nb_error
            nb_doublon += detector.nb_doublon

        # Update vars
        self.total_quads += int(nb_quads)
        self.total_tags_selected += int(nb_selected)
        self.total_tags_all += int(nb_detected)
        self.total_error += int(nb_error)
        self.total_success += int(nb_success)
        self.total_doublon += int(nb_doublon)
        self.total_drops += int(drops)
        self.legend['text'] = 'Quad: {:6}    Tag: {:6} ({:4}%)    '.format(self.total_quads, self.total_tags_all, round(100*(self.total_tags_all/(self.total_quads+1e-8)), 1))
        self.legend['text'] += 'Unique: {:6} ({:4}%)    '.format(self.total_tags_selected, round(100*self.total_tags_selected/(self.total_tags_all), 1))
        self.legend['text'] += 'Doublon: {:6} ({:4}%)    Success: {:6} ({:4}%)    Error: {:6} ({:4}%)    Drop: {:6} ({:4}%)'.format(self.total_doublon, round(100*self.total_doublon/(self.total_tags_all), 1), self.total_success, round(100*self.total_success/(self.total_success+self.total_error), 1), self.total_error, round(100*self.total_error/(self.total_success+self.total_error), 1),self.total_drops, round(100*(self.total_drops/(self.total_tags_selected+1e-8)), 1))
        self.prev_dropsPerTag = drops/nb_selected
        self.prev_tagPerQuads = nb_selected/nb_quads

    def update_plot(self, cameras, detectors, seconds):
        w, h = 30, 30
        if self.tag_channels:
            if not self.current_tagid:
                self.select_tag(self.tag_channels.keys()[0])
                self.tag_focus = {}
                self.tag_focus['group'] = tk.LabelFrame(self.tag_focus_group, bd=0, bg="white")
                self.tag_focus['group'].pack(fill=tk.BOTH, expand=1)
                self.tag_focus['imgroup'] = tk.LabelFrame(self.tag_focus['group'])
                self.tag_focus['imgroup'].pack(side=tk.LEFT)
                self.tag_focus['image'] = tk.Label(self.tag_focus['imgroup'])
                self.tag_focus['image'].pack(side=tk.TOP)
                self.tag_focus['ref_img'] = tk.Label(self.tag_focus['imgroup'])
                self.tag_focus['ref_img'].pack()
                self.tag_focus['descr'] = tk.Label(self.tag_focus['group'], text = '', bg="white")
                self.tag_focus['descr'].pack(fill=tk.X, expand=1, side=tk.LEFT)
                self.tag_focus['tag_btn'] = ttk.Button(self.tag_focus['group'], text = 'More', command = lambda: self.tag_window(self.current_tagid))
                self.tag_focus['tag_btn'].pack(fill=tk.X, side=tk.LEFT)
            for cam_id, detector in detectors.items():
                if not detector.online:
                    continue
                if self.current_tagid in detector.markers_dict.keys():
                    if not self.curr_tag_X and not self.curr_tag_Y:
                        self.curr_tag_X, self.curr_tag_Y = detector.positions[self.current_tagid][0]
                    tag_X, tag_Y = detector.positions[self.current_tagid][0]
                    drop = self.draw_plot(seconds, tag_X, tag_Y, detector.previous_tags)
                    self.curr_tag_drop += int(drop)
                    self.curr_tag_X = tag_X
                    self.curr_tag_Y = tag_Y
                    self.tag_focus_legend['text'] = "Drop: {}".format(self.curr_tag_drop)
                    self.tag_focus['descr']['text'] = "Tag {}\n Position X:{:4}, Position Y:{:4}\nRunning Time (seconds): {}\nCamera: {}".format(str(self.current_tagid), detector.positions[self.current_tagid][0][0], detector.positions[self.current_tagid][0][1], round(detector.detect_time[self.current_tagid], 1), ', '.join([cam[-8:-1] for cam in detectors.keys() if self.current_tagid in detectors[cam].markers_dict.keys()]))
                    # Update images
                    frame = detector.homothetie_markers[self.current_tagid]
                    self.update_image(frame, self.tag_focus['image'], w, h)
                    # Update ref_images
                    frame = detector.refs[0][self.current_tagid]*255
                    self.update_image(frame, self.tag_focus['ref_img'], w, h)

    def update(self, cameras, detectors, seconds):
        self.update_fps(seconds)
        self.update_markers(detectors, seconds)
        self.update_cameras(cameras, detectors, seconds)
        self.update_info(cameras, detectors, seconds)
        self.update_plot(cameras, detectors, seconds)
        self.info_txt['text'] = "Active Camera: {}, Tag Amount: {}, Mode: {}, Running Time: {}".format(len(cameras), len(set([marker_id for detector in detectors.values() for marker_id in detector.markers_dict.keys()])), self.mode.capitalize(), round(self.timer,1))
        #for cam_id, detector in detectors.items():
        #    self.info_txt['text'] += cam_id[-10:-1]+ " ::: {} ({}) ::: {} ({})".format(int(detector.method1), round(100*(detector.method1-detector.method1_error)/detector.method1, 2), int(detector.method2), round(100*(detector.method2-detector.method2_error)/detector.method2, 2))
        if self.tag_app:
            self.tag_app.update(seconds, cameras, detectors)

    def tag_window(self, marker_id):
        self.tagWindow = tk.Toplevel(self.master)
        self.tag_app = TagWindow(self.tagWindow, self, marker_id)

class TagWindow(Window):
    def __init__(self, master, main, marker_id):
        self.master = master
        self.main = main
        self.current_tagid = marker_id
        self.frame = tk.Frame(self.master)
        self.tag_channels = {}
        self.tag_log = []
        self.timer = 0
        self.setup()
        self.quitButton = ttk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.curr_tag_X = 0
        self.curr_tag_Y = 0
        self.total_drops = 0
        self.mean_drops = 0

    def setup(self):
        self.main_group = tk.LabelFrame(self.frame)
        self.main_group.pack(fill=tk.BOTH, expand=1)
        self.left_group = tk.LabelFrame(self.main_group)
        self.left_group.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.right_group = tk.LabelFrame(self.main_group)
        self.right_group.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)
        #markers
        self.tag_channel_group = tk.LabelFrame(self.left_group)
        self.tag_channel_group.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.create_tag_channel(self.current_tagid)
        # Tag list
        self.changetag_group = tk.LabelFrame(self.left_group)
        self.changetag_group.pack(fill=tk.BOTH, expand=1)
        self.listbox_group = tk.LabelFrame(self.changetag_group)
        self.listbox_group.pack(fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.listbox_group)
        scrollbar.pack(side = tk.RIGHT, fill=tk.Y)
        self.tag_list = tk.Listbox(self.listbox_group, yscrollcommand=scrollbar.set)
        self.tag_list.pack(fill=tk.BOTH, expand=1)
        scrollbar.config( command = self.tag_list.yview )
        self.valid_changetag_btn = ttk.Button(self.changetag_group, text = 'Change view', width = 25, command = self.close_windows)
        self.valid_changetag_btn.pack()
        # Add plot
        self.adv_group = tk.LabelFrame(self.right_group)
        self.adv_group.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)
        ## create a label in the frame
        descr = tk.Label(self.adv_group, text='Tag {} (X time; Y: the position x of the robot in the image)'.format(self.current_tagid))
        descr.pack()
        self.figure_Xpos, self.subplot_Xpos = self.add_plot(self.adv_group)
        self.figure_Ypos, self.subplot_Ypos = self.add_plot(self.adv_group)
        self.legend = tk.Label(self.adv_group, text='', bd=1)
        self.legend.pack()

    def create_tag_channel(self, marker_id):
        self.tag_channels[marker_id] = {}
        self.tag_channels[marker_id]['group'] = tk.LabelFrame(self.tag_channel_group)
        self.tag_channels[marker_id]['group'].pack(fill=tk.X, expand=1)
        self.tag_channels[marker_id]['imgroup'] = tk.LabelFrame(self.tag_channels[marker_id]['group'])
        self.tag_channels[marker_id]['imgroup'].pack(side=tk.LEFT)
        self.tag_channels[marker_id]['image'] = tk.Label(self.tag_channels[marker_id]['imgroup'])
        self.tag_channels[marker_id]['image'].pack(side=tk.TOP)
        self.tag_channels[marker_id]['ref_img'] = tk.Label(self.tag_channels[marker_id]['imgroup'])
        self.tag_channels[marker_id]['ref_img'].pack()
        self.tag_channels[marker_id]['descr'] = tk.Label(self.tag_channels[marker_id]['group'], text = '')
        self.tag_channels[marker_id]['descr'].pack(fill=tk.X, expand=1)
        self.tag_channels[marker_id]['tag_btn'] = ttk.Button(self.tag_channels[marker_id]['group'], text = 'More..')
        self.tag_channels[marker_id]['tag_btn'].pack(fill=tk.X, expand=1, side=tk.BOTTOM)

    def close_window(self):
        self.destroy()

    def update_list(self, tag_id):
        self.tag_list.insert(tk.END, "Tag " + str(tag_id))

    def update(self, seconds, cameras, detectors):
        self.timer += seconds
        w, h = 40, 40
        for cam_id, detector in detectors.items():
            if not detector.online:
                continue

            for marker_id, marker in detector.markers_dict.items():
                if not marker_id in self.tag_log and detector.detect_time[marker_id] > 0.5:
                    self.update_list(marker_id)
                    self.tag_log.append(marker_id)

                if not marker_id == self.current_tagid:
                    continue

                tag_X = detector.positions[marker_id][0][0]
                tag_Y = detector.positions[marker_id][0][1]
                if marker_id in detector.previous_tags:
                    self.tag_channels[marker_id]['descr']['text'] = "Tag {}\n{},{}\n{}sec\n(Active)".format(str(marker_id), tag_X, tag_Y, round(detector.detect_time[marker_id], 1))
                else:
                    self.tag_channels[marker_id]['descr']['text'] = "Tag {}\n{},{}\n{}sec\n(Inactive)".format(str(marker_id), tag_X, tag_Y, round(detector.detect_time[marker_id], 1))
                # Update images
                frame = detector.homothetie_markers[marker_id]
                self.update_image(frame, self.tag_channels[marker_id]['image'], w, h)
                # Update ref_images
                frame = detector.refs[0][marker_id]*255
                self.update_image(frame, self.tag_channels[marker_id]['ref_img'], w, h)
                self.draw_plot(seconds, tag_X, tag_Y, detector.previous_tags)
                self.curr_tag_X = tag_X
                self.curr_tag_Y = tag_Y

class Interface(object):
    def __init__(self, title):
        self.root = tk.Tk()
        ttk.Style().configure("TButton", padding=0, relief="flat",
           background="#ccc", width=5)
        #self.root.tk.call('tk', 'scaling', 1.466)
        self.root.title(title)
        self.app = MainWindow(self.root, title)
        self.root.protocol("WM_DELETE_WINDOW", self.kill)
        self.alive = True

    def update(self, cameras, detectors, seconds):
        self.app.update(cameras, detectors, seconds)
        self.root.update()
        #self.root.update_idletasks()

    @property
    def exit(self):
        return self.alive == False

    def kill(self):
        self.alive = False
        #self.root.destroy()
        self.root.quit()
        cv2.destroyAllWindows()
