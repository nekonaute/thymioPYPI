from PIL import Image, ImageTk
import Tkinter as tk
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
        frame = cv2.resize(frame, (h, w), interpolation=cv2.INTER_NEAREST)
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
        self.timer = 0
        self.framerate = None # label
        self.channels = {}
        self.tag_channels = {}
        self.mode = 'markers'
        self.marker_app = None
        self.master = master
        self.frame = tk.Frame(self.master)
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
        self.adv_button = tk.Button(self.frame, text = 'New Window', width = 25, command = self.tag_window)
        self.setup()
        #self.adv_button.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)

    def setup(self):
        self.main_group = tk.LabelFrame(self.frame)
        self.main_group.pack(fill=tk.BOTH, expand=1)
        self.left_group = tk.LabelFrame(self.main_group)
        self.left_group.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.right_group = tk.LabelFrame(self.main_group)
        self.right_group.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)
        #cameras
        self.camera_group = tk.LabelFrame(self.left_group)
        self.camera_group.pack(side=tk.LEFT,anchor=tk.NW)
        buttons_frame = tk.LabelFrame(self.camera_group)
        infos = [("original", 1), ("canny", 1), ("fgmask", 1), ("edges", 1), ("markers", 1), ("path", 1)]
        for mode, height in infos:
            tk.Button(buttons_frame, text=mode.capitalize(), command=lambda mode=mode: self.switch_mode(mode), height=height).pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        buttons_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.channel_group = tk.LabelFrame(self.camera_group)
        self.channel_group.pack(side=tk.LEFT)
        #markers
        self.tag_channel_group = tk.LabelFrame(self.right_group)
        self.tag_channel_group.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # Plots
        # scrollbar = tk.Scrollbar(self.right_group)
        # scrollbar.pack(side = tk.RIGHT, fill=tk.Y)
        # self.plot_group = tk.LabelFrame(self.right_group)
        # self.plot_group.pack(fill=tk.BOTH, expand=1, side=tk.BOTTOM)
        #scrollbar.config()
        ### create a label in the frame
        #descr = tk.Label(self.plot_group, text='Drops through time (X time; Y: Drops count)')
        #descr.pack()
        # self.figure_tagPerQuads, self.subplot_tagPerQuads = self.add_plot(self.plot_group)
        # self.legend_tagPerQuads = tk.Label(self.plot_group, text='Tags per Quads through time (X time; Y: Tags/Quads)')
        # self.legend_tagPerQuads.pack()
        # self.figure_dropsCount, self.subplot_dropsCount = self.add_plot(self.plot_group)
        # self.legend_dropsCount = tk.Label(self.plot_group, text='Drops through time (X time; Y: Drops count)')
        # self.legend_dropsCount.pack()
        # self.figure_dropsPerTag, self.subplot_dropsPerTag = self.add_plot(self.plot_group)
        # self.legend_dropsPerTag = tk.Label(self.plot_group, text='Drops/TagAmount through time (X time; Y: Drops count)')
        # self.legend_dropsPerTag.pack()
        self.legend = tk.Label(self.frame, text='Drops: N/A    Quads: N/A    Tag : N/A    Drop/Tag : N/A%')
        self.legend.pack()
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
        self.tag_channels[marker_id]['descr'].pack(fill=tk.X, expand=1)
        self.tag_channels[marker_id]['tag_btn'] = tk.Button(self.tag_channels[marker_id]['group'], text = 'More..', command = lambda: self.tag_window(marker_id))
        self.tag_channels[marker_id]['tag_btn'].pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        self.tag_channel_group.columnconfigure(c, weight=1)

    def update_fps(self, seconds):
        # Calculate frames per second
        self.timer += seconds
        self.fps  = 1 / seconds
        self.fps_mean = self.fps_mean + (self.fps - self.fps_mean)
        self.master.title(self.title + ' - FPS: {} (avg. {})'.format(min(60,round(self.fps, 1)), min(60,round(self.fps_mean, 1))))

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
            if not detector.online:
                continue
            if not cam_id in self.channels.keys():
                self.create_channel(cam_id)
            # Update texts
            self.channels[cam_id]['descr']['text'] = 'cam {} {} {} tags {}'.format(str(cam_id)[-8:-1], " "*10, int(detector.nb_selected), detector.detected)
            # Update images
            frame = detectors[cam_id].get(self.mode).copy()
            w, h = frame.shape[:2]
            w, h = max(w-w*70/100, 200), max(h-h*70/100, 300)
            self.update_image(frame, self.channels[cam_id]['image'], h, w)

    def update_plots(self, cameras, detectors, seconds):
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

        # # Draw
        # self.subplot_tagPerQuads.plot([self.timer-seconds, self.timer], [self.prev_tagPerQuads, (nb_selected-1e-6)/nb_quads], 'r-')
        # self.figure_tagPerQuads.canvas.draw()
        # self.subplot_dropsCount.plot([self.timer-seconds, self.timer], [self.total_drops, self.total_drops+drops], 'r-', linewidth=2)
        # self.figure_dropsCount.canvas.draw()
        # self.subplot_dropsPerTag.plot([self.timer-seconds, self.timer], [self.prev_dropsPerTag, drops/nb_selected], 'r-', linewidth=2)
        # self.figure_dropsPerTag.canvas.draw()

        # Update vars
        self.total_quads += int(nb_quads)
        self.total_tags_selected += int(nb_selected)
        self.total_tags_all += int(nb_detected)
        self.total_error += int(nb_error)
        self.total_success += int(nb_success)
        self.total_doublon += int(nb_doublon)
        self.total_drops += int(drops)
        self.legend['text'] = 'Quad: {:6}    Tag: {:6} ({:4}%)    '.format(self.total_quads, self.total_tags_all, round(100*(self.total_tags_all/(self.total_quads+1e-8)), 1))
        self.legend['text'] += 'Doublon: {:6} ({:4}%)    Success: {:6} ({:4}%)    Error: {:6} ({:4}%)    Drop: {:6} ({:4}%)'.format(self.total_doublon, round(100*self.total_doublon/(self.total_tags_all), 1), self.total_success, round(100*self.total_success/(self.total_success+self.total_error), 1), self.total_error, round(100*self.total_error/(self.total_success+self.total_error), 1),self.total_drops, round(100*(self.total_drops/(self.total_tags_selected+1e-8)), 1))
        self.prev_dropsPerTag = drops/nb_selected
        self.prev_tagPerQuads = nb_selected/nb_quads

    def update(self, cameras, detectors, seconds):
        self.update_fps(seconds)
        self.update_markers(detectors, seconds)
        self.update_cameras(cameras, detectors, seconds)
        self.update_plots(cameras, detectors, seconds)
        self.info_txt['text'] = "Active Camera: {}, Tag Amount: {}, Mode: {}".format(len(cameras), len(set([marker_id for detector in detectors.values() for marker_id in detector.markers_dict.keys()])), self.mode.capitalize())
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
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
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
        self.valid_changetag_btn = tk.Button(self.changetag_group, text = 'Change view', width = 25, command = self.close_windows)
        self.valid_changetag_btn.pack()
        # Add plot
        self.adv_group = tk.LabelFrame(self.right_group)
        self.adv_group.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)
        ## create a label in the frame
        descr = tk.Label(self.adv_group, text='Tag {} (X time; Y: the position x of the robot in the image)'.format(self.current_tagid))
        descr.pack()
        self.figure_Xpos, self.subplot_Xpos = self.add_plot(self.adv_group)
        self.figure_Ypos, self.subplot_Ypos = self.add_plot(self.adv_group)
        self.legend = tk.Label(self.adv_group, text='Drops: N/A')
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
        self.tag_channels[marker_id]['tag_btn'] = tk.Button(self.tag_channels[marker_id]['group'], text = 'More..')
        self.tag_channels[marker_id]['tag_btn'].pack(fill=tk.X, expand=1, side=tk.BOTTOM)

    def update_plot(self, seconds, tag_X, tag_Y, previous_tags):
        self.timer += seconds
        if self.timer > seconds:
            if not self.current_tagid in previous_tags:
                self.subplot_Xpos.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], 'ro')
                self.subplot_Ypos.plot([self.timer-seconds, self.timer], [self.curr_tag_Y, tag_Y], 'ro')
                self.total_drops += 1
                #self.a.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], [self.curr_tag_Y, tag_Y], 'ro', linewidth=2)
            else:
                self.subplot_Xpos.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], 'g-')
                self.subplot_Ypos.plot([self.timer-seconds, self.timer], [self.curr_tag_Y, tag_Y], 'g-')
                #self.a.plot([self.timer-seconds, self.timer], [self.curr_tag_X, tag_X], [self.curr_tag_Y, tag_Y], 'g-', linewidth=2)
            self.figure_Xpos.canvas.draw()
            self.figure_Ypos.canvas.draw()
            self.legend['text'] = 'Drops: {}'.format(self.total_drops)

    def close_window(self):
        self.destroy()

    def update_list(self, tag_id):
        self.tag_list.insert(tk.END, "Tag " + str(tag_id))

    def update(self, seconds, cameras, detectors):
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
                self.update_plot(seconds, tag_X, tag_Y, detector.previous_tags)
                self.curr_tag_X = tag_X
                self.curr_tag_Y = tag_Y

class Interface(object):
    def __init__(self, title):
        self.root = tk.Tk()
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
