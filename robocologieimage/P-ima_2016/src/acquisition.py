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
        if (ret == False): # failed to capture
            if not self.done:
                print "Camera ended (type={}, id={})".format(type(self.id), self.id)
            done = True
            return done, np.zeros((360,640, 3), np.uint8)
        w, h = frame.shape[:2]
        #w, h = max(w-w*30/100, 200), max(h-h*30/100, 300)
        frame = cv2.resize(frame, (h, w), interpolation=cv2.INTER_AREA)
        done = False
        cv2.waitKey(0)
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
            self.device = cv2.VideoCapture(self.id)
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

class Kinect(Material):
    def __init__(self, capture_id):
        super(Kinect, self).__init__(capture_id)
        self.active = False

    def next(self):
        done = True
        frame,_ = freenect.sync_get_video(self.id)
        frame = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        cv2.waitKey(0)
        if frame:
            done = False
        return done, frame

    def open(self):
        try:
            array,_ = freenect.sync_get_video(self.id)
            array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
        except cv2.error as e:
            print "Camera not connected (id={})".format(self.id)
            self.active = False
        else:
            print "New camera added (id={})".format(self.id)
        self.active = True
