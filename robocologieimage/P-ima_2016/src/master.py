 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from utilities import get_refs
from interface import Interface
from acquisition import Controller
from detection import Detector
import time
import cv2
import numpy as np

class Master(object):
    def __init__(self, title, reference):
        # Get program start time for framerate visualization
        self.start_time = time.time()
        self.running_time = 0

        # Main objects
        self.interface = None
        self.controller = None
        self.detectors = {}

        # Give a title + descr
        self.title = title
        self.ref_title = reference

    def setup_controller(self, mode, list_capture_id):
        # Controller manage I/O with cameras or movie files (see mode)
        self.controller = Controller(mode, list_capture_id)
        self.list_capture_id = list_capture_id
        self.mode = mode

    def setup_detectors(self, list_reference_tag, classifier = [], list_valid_tags = []):
        # Each camera have its own Detector engine
        self.detectors = {cam_id : Detector(list_reference_tag) for i, cam_id in enumerate(self.list_capture_id)}

    def setup_interface(self, with_GUI):
        # Interface use Tkinter for scene and detection visualization
        if with_GUI:
            self.interface = Interface(self.title)

    def run(self):
        seconds = 1e-6
        out = None
        # Check if any camera is broadcasting and no exit call asked
        while True:
            # If exit call break the loop
            if self.interface and self.interface.exit:
                break
            elif not self.interface and not self.controller.active:
                break

            if self.interface.getState() == "MainWindow":
                if self.interface.isRecording() and not out:
                    #print("Once only")
                    #out = cv2.VideoWriter(self.interface.getRecordId() + ".avi", -1, 20.0, (640,480))
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    out = cv2.VideoWriter(self.interface.getRecordId() + ".avi",fourcc, 20.0, (640,480))
                # Update controller for new images
                self.controller.update()
                # Collect broadcasting cameras
                live_cams = self.controller.getActive()
                # Collect Parameters
                parameters = self.interface.app.parameters
                for cam_id, cam in live_cams.items():
                    # Select the camera assigned detector
                    detector = self.detectors[cam_id]
                    # Run detection on next frame and update state
                    detector.update(cam.frame, parameters, seconds)
                # Collect offline cameras
                offline_cams = self.controller.getDeactive()
                for cam_id, cam in offline_cams.items():
                    # Announce camera is now offline
                    self.detectors[cam_id].online = False
                # Update Tkinter interface using cameras and detectors infos
                self.interface.update(live_cams, self.detectors, seconds, out)
            else:
                self.interface.update()
            # Update timer and compute framerate
            seconds = self.updateTime() + 1e-6
            fps = 1 / seconds
        out.release()

    def updateTime(self):
        # End time
        end = time.time()
        # Time elapsed
        seconds = end - self.start_time
        # Start time
        self.start_time = time.time()
        self.running_time +=  seconds
        return seconds

    def collect_data(self, npzfilename):
        """ Collect data from detector for learning purpose """

        # Set minimum detection time threshold (good against false-positives)
        MIN_DETECT_TIME = 2.0

        labels = []
        data = []
        for cam_id, detector in self.detectors.items():
            for tag, images in detector.images_stock.items():
                if detector.detect_time.get(tag, 0) < MIN_DETECT_TIME and not tag == -1:
                    continue
                if tag == -1:
                    print "2", tag, len(data)
                for image in images:
                    data.append(image)
                    labels.append(tag)
        labels = np.array(labels)
        data = np.array(data)
        np.savez("../data/npz/{}".format(npzfilename), labels, data)

    def kill(self):
        self.interface.kill()
        self.controller.killAll()
