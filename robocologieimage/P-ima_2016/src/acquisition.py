 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import cv2
import numpy as np

class Material(object):
    def __init__(self, id_):
        """ id_ - Filepath or Camera Index """
        self.id = id_
        self.frame = None
        self.results = {}
        self.done = False

    def next(self):
        ret, frame = self.device.read()
        print frame
        if (ret == False): # failed to capture
            if not self.done:
                print "Camera ended (id={})".format(self.id)
            done = True
            return done, np.zeros((360,640, 3), np.uint8)
        w, h = frame.shape[:2]
        #w, h = max(w-w*30/100, 200), max(h-h*30/100, 300)
        frame = cv2.resize(frame, (h, w), interpolation=cv2.INTER_AREA)
        done = False
        return done, frame

    def update(self):
        self.done, self.frame = self.next()

    def kill(self):
        """ Releases video capture device. """
        cv2.VideoCapture(self.id).release()

    def getFrame(self):
        return self.frame


class Video(Material):
    def __init__(self, video_id):
        super(Video, self).__init__(video_id)
        self.device = cv2.VideoCapture(self.id)
        self.active = False

    def open(self):
        self.active = True

class Camera(Material):
    def __init__(self, capture_id):
        super(Camera, self).__init__(capture_id)
        self.active = False

    def open(self):
        try:
            self.device = cv2.VideoCapture("../data/video/kinect/v2kinect04-29-27.mp4")
        except cv2.error as e:
            print "Camera not connected (id={})".format(self.id)
            self.active = False
        else:
            print "New camera added (id={})".format(self.id)
            self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, 600*2);
            self.device.set(cv2.CAP_PROP_FRAME_WIDTH, 800*2);
            self.device.set(cv2.CAP_PROP_FPS, 30);
            print "Parameters: {}x{} fps={}".format(int(self.device.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.device.get(cv2.CAP_PROP_FRAME_HEIGHT)), self.device.get(cv2.CAP_PROP_FPS))
        self.active = True

    def update(self):
        super(Camera, self).update()

class Controller(object):
    def __init__(self, captures):
        assert isinstance(captures, list)
        self.captures = {}
        for capture_id in captures:
            try:
                capture_id = int(capture_id)
            except ValueError:
                self.captures[capture_id] = Video(capture_id)
            else:
                self.captures[capture_id] = Camera(capture_id)


    def kill(self, ids):
        """
        Kill captures whose identifier is found in `capture_list`.
        capture_list : capture object list
        """
        for capture_id in ids:
            self.captures[capture_id].kill()

    def addCamera(self, capture_id):
        if capture_id in self.captures.keys():
            return False
        self.captures[capture_id] = Camera(capture_id)
        return True

    def openCaptures(self):
        for capture_id in self.captures:
            capture = self.captures[capture_id]
            if not capture.active:
                capture.open()

    def getAll(self):
        return {capture_id : cam for capture_id, cam in self.captures.items()}

    def killAll(self):
        self.kill(self.captures.keys())

    def getActive(self):
        online_captures = {}
        for capture_id, capture in self.captures.items():
            #print(not capture.done, capture.active)
            if not capture.done and capture.active:
                online_captures[capture_id] = capture
        return online_captures

    def getDeactive(self):
        offline_captures = {}
        for capture_id, capture in self.captures.items():
            if capture.done or not capture.active:
                offline_captures[capture_id] = capture
        return offline_captures

    def update(self):
        live_cams = self.getActive()
        for capture_id, cam in live_cams.items():
            cam.update()

    @property
    def active(self):
        return len(self.getActive().values()) != 0
