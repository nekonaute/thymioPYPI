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
                print "Camera ended (id={})".format(self.id)
            done = True
            return done, np.zeros((360,640, 3), np.uint8)
        w, h = frame.shape[:2]
        #w, h = max(w-w*30/100, 200), max(h-h*30/100, 300)
        #frame = cv2.resize(frame, (h, w), interpolation=cv2.INTER_AREA)
        done = False
        return done, frame

    def update(self):
        self.done, self.frame = self.next()

    def kill(self):
        """ Releases video capture device. """
        cv2.VideoCapture(self.id).release()

class Video(Material):
    def __init__(self, video_id):
        super(Video, self).__init__(video_id)
        self.device = cv2.VideoCapture(self.id)
        self.active = True

class Camera(Material):
    def __init__(self, cam_id):
        super(Camera, self).__init__(cam_id)
        self.active = self.open()

    def open(self):
        try:
            self.device = cv2.VideoCapture(self.id)
        except cv2.error as e:
            print "Camera not connected (id={})".format(self.id)
            return False
        else:
            print "New camera added (id={})".format(self.id)
            self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, 600*2);
            self.device.set(cv2.CAP_PROP_FRAME_WIDTH, 800*2);
            self.device.set(cv2.CAP_PROP_FPS, 30);
            print "Parameters: {}x{} fps={}".format(int(self.device.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.device.get(cv2.CAP_PROP_FRAME_HEIGHT)), self.device.get(cv2.CAP_PROP_FPS))
        return True

    def update(self):
        super(Camera, self).update()

class Controller(object):
    def __init__(self, ids, mode):
        assert isinstance(ids, tuple)
        if mode == 'CAMERA':
            self.cameras = {camid : Camera(camid) for camid in ids}
        elif mode == 'VIDEO':
            self.cameras = {camid : Video(camid) for camid in ids}

    def kill(self, ids):
        """
        Kill cameras whose identifier is found in `camera_list`.
        camera_list : camera object list
        """
        for cam_id in ids:
            self.cameras[cam_id].kill()

    def addCamera(self, cam_id):
        if cam_id in self.cameras.keys():
            return False
        self.cameras[cam_id] = Camera(cam_id)
        return True

    def openCamera(self, cam_id):
        assert cam_id in self.cameras.keys()
        camera = self.cameras[cam_id]
        if not camera.active:
            camera.active = camera.open()
        return camera.active

    def getAll(self):
        return {cam_id : cam for cam_id, cam in self.cameras.items()}

    def killAll(self):
        self.kill(self.cameras.keys())

    def getActive(self):
        return {cam_id: cam for cam_id, cam in self.cameras.items() if not cam.done and cam.active}

    def update(self, new_cam_ids=[]):
        for cam_id in new_cam_ids:
            exist = self.addCamera(cam_id)
            if not exist:
                self.openCamera(cam_id)

        live_cams = self.getActive()
        for cam_id, cam in live_cams.items():
            cam.update()

    @property
    def active(self):
        return len(self.getActive().values()) != 0
