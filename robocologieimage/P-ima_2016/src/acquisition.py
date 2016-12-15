 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import cv2
import numpy as np
import freenect
import random

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
    ctx = freenect.init()

    def __init__(self, capture_id):
        super(Kinect, self).__init__(capture_id)
        self.active = False

    def next(self):
        done = True
        frame,_ = freenect.sync_get_video(self.id)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # undistort
        h, w = frame.shape[:2]
        K = np.array([[6526.37013657, 0.00000000, 313.68782938], [0.00000000, 526.37013657, 259.01834898,], [0.00000000, 0.00000000, 1.00000000 ]])
        d = np.array([0.18126525, -0.39866885, 0.00000000, 0.00000000, 0.00000000]) # just use first two terms (no translation)
        newcamera, roi = cv2.getOptimalNewCameraMatrix(K, d, (w,h), 0)
        frame = cv2.undistort(frame, K, d, None, newcamera)
        cv2.waitKey(0)
        if frame is not None:
            done = False
        return done, frame

    def open(self):
        try:
            ctx = freenect.init()
            self.device = freenect.open_device(self.ctx, self.id)
            freenect.set_led(self.device, 1)
            #freenect.set_video_mode(self.device, freenect.RESOLUTION_HIGH, freenect.VIDEO_RGB)
            #freenect.set_depth_mode(self.device, freenect.RESOLUTION_HIGH, freenect.DEPTH_REGISTERED)
            freenect.close_device(self.device)
        except cv2.error as e:
            print "Camera not connected (id={})".format(self.id)
            self.active = False
        else:
            frame,_ = freenect.sync_get_video(self.id)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            w, h = frame.shape[:2]
            print "New camera added (id={}, size={}x{})".format(self.id, w, h)
        self.active = True
