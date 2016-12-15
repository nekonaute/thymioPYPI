 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from acquisition import Video
from acquisition import Camera, Kinect

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
                # self.captures[capture_id] = Camera(capture_id)
                self.captures[capture_id] = Kinect(capture_id)
        print(self.captures)

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
