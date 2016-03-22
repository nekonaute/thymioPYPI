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
        self.detectors = {cam_id : Detector(list_reference_tag, classifier, list_valid_tags[i]) for i, cam_id in enumerate(self.list_capture_id)}

    def setup_interface(self, with_GUI):
        # Interface use Tkinter for scene and detection visualization
        if with_GUI:
            self.interface = Interface(self.title)

    def run(self):
        seconds = 1e-6
        # Check if any camera is broadcasting and no exit call asked
        while self.controller.active:
            if self.interface and self.interface.exit:
                break
            # Update controller for new images
            self.controller.update()
            # Collect broadcasting cameras
            live_cams = self.controller.getActive()
            for cam_id, cam in live_cams.items():
                # Select the camera assigned detector
                detector = self.detectors[cam_id]
                # Run detection on next frame and update state
                detector.update(cam.frame, seconds)
            if self.interface:
                # Update Tkinter interface using cameras and detectors infos
                self.interface.update(live_cams, self.detectors, seconds)
            # Update timer and compute framerate
            seconds = self.updateTime()
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

        #
        labels = []
        data = []
        for cam_id, detector in self.detectors.items():
            for tag, images in detector.images_stock.items():
                if detector.detect_time.get(tag, 0) < MIN_DETECT_TIME:
                    continue
                for image in images:
                    data.append(images)
                    labels.append(tag)
        labels = np.array(labels)
        data = np.array(data)
        np.savez("../data/npz/{}".format(npzfilename), labels, data)

    def evaluation(self):
        detected = [1e-6 for _ in self.detectors.values()[0].method]
        error = [1e-6 for _ in self.detectors.values()[0].method]
        correct = [1e-6 for _ in self.detectors.values()[0].method]
        unsure = [1e-6 for _ in self.detectors.values()[0].method]
        for _, detector in self.detectors.items():
            for i, method in enumerate(detector.method):
                detected[i] += int(method['detected'])
                error[i] += int(method['error'])
                correct[i] += int(method['success'])
                unsure[i] += int(method['unsure'])

        error_perc = [.0 for _ in self.detectors.values()[0].method]
        correct_perc = [.0 for _ in self.detectors.values()[0].method]
        unsure_perc  = [.0 for _ in self.detectors.values()[0].method]
        total_detected, total_correct, total_error, total_unsure = 1e-6, .0, .0, .0
        total_correct_perc, total_error_perc, total_unsure_perc  = (.0,)*3
        for i, method in enumerate(detector.method):
            correct_perc[i] = round(100.0*correct[i]/detected[i], 2)
            error_perc[i] = round(100.0*error[i]/detected[i], 2)
            unsure_perc[i] = round(100.0*unsure[i]/detected[i], 2)
            total_detected += detected[i]
            total_correct += correct[i]
            total_error += error[i]
            total_unsure += unsure[i]
        total_correct_perc = round(100.0*total_correct/total_detected, 2)
        total_error_perc = round(100.0*total_error/total_detected, 2)
        total_unsure_perc = round(100.0*total_unsure/total_detected, 2)
        print self.ref_title
        for i, method in enumerate(detector.method):
            print "::{}:: {:.0f} (Total) {:.0f} (Correct {}%) {:.0f} (Error {}%) {:.0f} (Maybe {}%)".format(i+1, detected[i], correct[i], correct_perc[i], error[i], error_perc[i], unsure[i], unsure_perc[i])
        print "::T:: {:.0f} (Total) {:.0f} (Correct {}%) {:.0f} (Error {}%) {:.0f} (Maybe {}%)\n::Running Time:: {:.0f}s".format(total_detected, total_correct, total_correct_perc, total_error, total_error_perc, total_unsure, total_unsure_perc, self.running_time)

    def kill(self):
        self.interface.kill()
        self.controller.killAll()
