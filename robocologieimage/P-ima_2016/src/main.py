 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from utilities import get_refs
from interface import Interface
from acquisition import Controller
from detection import Detector
import time
import cv2
import numpy as np

# Do not modify
VIDEO = 'VIDEO'
CAMERA = 'CAMERA'

# Edit here
ID_CAMERA = (1,)
ID_VIDEO1 = ('../data/video/sony/vid_00.mp4', '../data/video/sony/vid_01.mp4', '../data/video/asus/vid_00.mp4', '../data/video/asus/vid_01.mp4', '../data/video/asus/vid_02.mp4')
ID_VIDEO2 = ('../data/video/kinect/2016-03-07-155725.webm',)
REFS_CAMERA = get_refs("../data/ref_markers_512bits.json")
REFS_VIDEO = get_refs("../data/ref_markers_16bits.json")
PROJECT_TITLE = "PIMA (2016) - Multiple Camera Robot Detection"

# Edit mode
V1 = (CAMERA, ID_CAMERA, REFS_CAMERA)
V2 = (VIDEO, ID_VIDEO1, REFS_VIDEO)
V3 = (VIDEO, ID_VIDEO2, REFS_CAMERA) #KINECT
CURRENT_MODE, CURRENT_ID, CURRENT_REFS = V3

class Master(object):
    def __init__(self, mode, ids):
        # Get program start time for framerate visualization
        self.start_time = time.time()
        # Interface use Tkinter for scene and detection visualization
        self.interface = Interface(PROJECT_TITLE)
        # Controller manage I/O with cameras or movie files (see mode)
        self.controller = Controller(ids, mode)
        # Each camera have its own Detector engine
        self.detectors = {cam_id : Detector(CURRENT_REFS) for cam_id in ids}

    def run(self):
        seconds = 1e-6
        # Check if any camera is broadcasting and no exit call asked
        while self.controller.active and not self.interface.exit:
            #cv2.imshow("wait", np.array([[0],[0]]))
            #cv2.waitKey(1)
            # Update controller for new images
            self.controller.update()
            # Collect broadcasting cameras
            live_cams = self.controller.getActive()
            for cam_id, cam in live_cams.items():
                # Select the camera assigned detector
                detector = self.detectors[cam_id]
                # Run detection on next frame and update state
                detector.update(cam.frame, seconds)
            # Update Tkinter interface using cameras and detectors infos
            self.interface.update(live_cams, self.detectors, seconds)
            #self.printFps()
            seconds = self.updateTime()

        for cam_id, detector in self.detectors.items():
            print cam_id[-10:-1]+ " ::: {} ({}) ::: {} ({})".format(int(detector.method1), round(100*(detector.method1-detector.method1_error)/detector.method1, 2), int(detector.method2), round(100*(detector.method2-detector.method2_error)/detector.method2, 2))

    def updateTime(self):
        # End time
        end = time.time()
        # Time elapsed
        seconds = end - self.start_time
        # Calculate frames per second
        fps  = 1 / seconds;
        # Start time
        self.start_time = time.time()
        return seconds

    def kill(self):
        self.interface.kill()
        self.controller.killAll()

if __name__ == "__main__":
    # Setup interface, controller and detectors according to mode and ids
    master = Master(CURRENT_MODE, CURRENT_ID)

    # Run the program
    master.run()

    # When everything done, kill tkinter interface and release all capture
    master.kill()
