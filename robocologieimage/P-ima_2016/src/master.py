 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import time
import cv2
import numpy as np

from interface import Interface
from controller import Controller
from detection import Detector

from interface_utilities import load_parameters, get_default_parameters
from utilities import get_refs

PREV_PARAM_FILENAME = "temp_parameters.json"
DEFAULT_PARAM_FILENAME = "default_parameters.json"

class Master(object):

    def __init__(self, title, reference):
        # Get program start time for framerate visualization
        self.start_time = time.time()
        self.running_time = 0
        self.if_record = False
        self.if_interface = False

        # Main objects
        self.interface = None
        self.controller = None
        self.output_video = None
        self.output_name = ""
        self.parameters = {}
        self.detectors = {}
        self.cameras = {}

        # Give a title + descr
        self.title = title
        self.ref_title = reference

    def setup_parameters(self):
        self.parameters.update(get_default_parameters())
        prev_parameters = load_parameters(PREV_PARAM_FILENAME)
        if prev_parameters:
            self.parameters.update(load_parameters(PREV_PARAM_FILENAME))
        else:
            print("Previous parameters not found !")
            default_parameters = load_parameters(DEFAULT_PARAM_FILENAME)
            if default_parameters:
                self.parameters.update(default_parameters)

    def setup_interface(self):
        # Interface use Tkinter for scene and detection visualization
        self.if_interface = True
        self.interface = Interface(self.title, self.parameters)

    def setup_preferences_gui(self):
        window_name = "StartWindow"
        window_type = self.interface.getStateType(window_name)
        self.interface.switchState(window_type)
        while self.interface.isOnline():
            self.interface.update()

    def setup_controller(self):
        # Controller manage I/O with cameras or movie files (see mode)
        captures = self.parameters['captures']
        self.controller = Controller(captures)

    def setup_detectors(self, default_references):
        # Each camera have its own Detector engine
        references = self.parameters.get('references', default_references)
        for capture_id in self.controller.captures:
            self.detectors[capture_id] = Detector(get_refs(references))

    def setup_detection_gui(self):
        window_name = "MainWindow"
        window_type = self.interface.getStateType(window_name)
        self.interface.switchState(window_type)

    def open_captures(self):
        self.controller.openCaptures()

    def initRecording(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.output_video = cv2.VideoWriter(self.output_name + ".avi", fourcc, 20.0, (640,480))

    def deactiveDetectors(self, offline_captures):
        for capture_id, cam in offline_captures.items():
            # Announce camera is now offline
            self.detectors[capture_id].online = False

    def updateInterface(self, live_cams, seconds):
        self.interface.update(live_cams, self.detectors, seconds, self.output_video)
        self.if_record = self.interface.isRecording()
        self.output_name = self.interface.getRecordId()
        self.parameters = self.interface.getParameters()

    def releaseAll(self):
        if self.output_video:
            self.output_video.release()

    def run(self):
        seconds = 1e-6
        online_captures = {}
        # Check if any camera is broadcasting and no exit call asked
        while True:
            if self.if_interface:
                # Update Tkinter interface using cameras and detectors infos
                self.updateInterface(online_captures, seconds)
            if self.if_record:
                # Start recording broadcast
                self.initRecording()
            # Update controller for new images
            self.controller.update()
            # Collect broadcasting cameras
            online_captures = self.controller.getActive()
            offline_captures = self.controller.getDeactive()
            self.deactiveDetectors(offline_captures)
            self.controller.kill(offline_captures)
            for capture_id, capture in online_captures.items():
                # Select the camera assigned detector
                detector = self.detectors[capture_id]
                # Run detection on next frame and update state
                frame = capture.getFrame()
                detector.update(frame, self.parameters, seconds)
            # Collect offline cameras
            # Update timer and compute framerate
            seconds = self.updateTime() + 1e-6
            fps = 1 / seconds

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
        self.releaseAll()
        self.interface.kill()
        self.controller.killAll()
