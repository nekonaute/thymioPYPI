import cv2
import numpy as np
import signal
import time
from datetime import datetime

import validation
from Image_Processor import Image_Processor
from Tag_Detector import Tag_Detector
import settings
import tag_recognition
import image_utils

global TESTING
global RUNNING
RUNNING = True
TESTING = False
VALIDATION = False

def signal_handler_stop_running(signal, frame):
    global RUNNING
    RUNNING = False

def signal_handler_test(signal, frame):
    global TESTING
    TESTING = True

if __name__ == '__main__':
    """
    Use this script to test the tag recogniotion on raspberry pi.
    """
    RUNNING = True
    # register signals
    #CTRL C
    signal.signal(signal.SIGINT, signal_handler_stop_running)
    #CTRL Z
    signal.signal(signal.SIGTSTP, signal_handler_test)

    tag_detection_experiment = Tag_Detector()
    tag_detection_experiment.start()
    print "CTRL-Z: show image\nCTRL-C shutdown\nallowing camera to warm up"
    time.sleep(2)
    print "let's start!"
    tags_info = None

    while(RUNNING):
        newresults, tags_info = tag_detection_experiment.get_results()
        tags_contours, tags_ids, tags_distances, tags_rotations = tags_info

        if newresults and len(tags_contours)>0:
            if VALIDATION:
                validation.update(tags_ids,tags_distances)
            message = 'distances: ' + `tags_distances`
            #message+= '\trotations: ' + `tags_rotations`
            message += '\tids: ' + `tags_ids`
            message+= datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print message

        if TESTING:
            TESTING = False
            if VALIDATION:
                validation.compute_stats()
            print validation.validation['tags']
            print "press any key to close window."
            tags_contours, tags_ids, tags_distances, tags_rotations = tags_info
            rgb_image = np.zeros((tag_detection_experiment.prec_frame.shape[0],tag_detection_experiment.prec_frame.shape[1],3),dtype=np.uint8)
            rgb_image[:,:,0] = tag_detection_experiment.prec_frame
            rgb_image[:,:,1] = rgb_image[:,:,0]
            rgb_image[:,:,2] = rgb_image[:,:,0]
            rgb_image = image_utils.draw_contours(rgb_image,tags_contours)
            image_utils.show_image(rgb_image)
    tag_detection_experiment.shutdown()
    if VALIDATION:
        validation.save_stats()
    print "good bye."
