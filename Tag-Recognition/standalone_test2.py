import cv2
import numpy as np
import signal
import time
from datetime import datetime

import validation
import Image_Processor
from Image_Processor import Detector
from Tag_Detector import Tag_Detector
import settings
import tag_recognition
from tag_recognition import CNT,IDS,DST,ROT
import image_utils

global TESTING
global RUNNING
global VALIDATION
global TRACKING_EVAL

RUNNING = True
TESTING = False
VALIDATION = False
TRACKING_EVAL = False
motion_EVAL = False

def center(poly4gone):
    cx = int((poly4gone[0][0][0] +  poly4gone[1][0][0] + poly4gone[2][0][0] + poly4gone[3][0][0])/4.0)
    cy = int((poly4gone[0][0][1] +  poly4gone[1][0][1] + poly4gone[2][0][1] + poly4gone[3][0][1])/4.0)
    return [cx,cy]

class Tag_Detector_Eval(Detector):
    def __init__(self, tag_settings = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]):
        Detector.__init__(self)
        self.tag_settings = tag_settings
        self.prec_frame = None
        self.tag_results = None
        self.color_image = None
        self.set_pre_processing_function(image_utils.convert_to_HSV)
        self.count_curr_frame = 0
        self.frame_buffer_size = 2
        self.positions = {}
        self.overlapp_image = None
        self.A_value = 0
        self.inter_dist = 0
        self.dist = 0

    def post_processing_function(self,image):
        area_ratio = self.tag_settings[settings.AREA_RATIO_KEY]
        actual_side_size = self.tag_settings[settings.SIDE_KEY]
        if self.count_curr_frame == 0:
            self.prec_frame = image[:,:,2]
            self.tag_results = tag_recognition.detect_tags(self.prec_frame ,area_ratio, actual_side_size=actual_side_size)
        elif self.count_curr_frame > 0:
            prec_ids = self.tag_results[IDS]
            prec_contours = self.tag_results[CNT]
            prec_frame = self.prec_frame
            curr_frame = image[:,:,2]
            if len(prec_contours)>0:
                status, next_contours, next_distances, next_rotations = tag_recognition.estimate_next_positions(prec_frame,curr_frame,prec_contours, actual_side_size=actual_side_size)
                ids = np.array(self.tag_results[IDS])[status==1]
                ST_results = next_contours, ids, next_distances, next_rotations
                ST_contours, ST_ids, ST_distances, ST_rotations = ST_results
                GT_results = tag_recognition.detect_tags(curr_frame, area_ratio, actual_side_size=actual_side_size)
                GT_contours, GT_ids, GT_distances, GT_rotations = GT_results
                for i in range(len(ST_ids)):
                    ST_tag_id, ST_tag_contour = ST_ids[i], ST_contours[i]
                    if ST_tag_id in GT_ids and ST_tag_id in prec_ids:
                        j = GT_ids.index(ST_tag_id)
                        GT_tag_contour = GT_contours[j]
                        self.GT_C = center(GT_tag_contour)
                        self.ST_C = center(ST_tag_contour)
                        self.GT_ST = [GT_tag_contour,ST_tag_contour]
                        self.A_value = validation.A_intersect(GT_tag_contour,ST_tag_contour,curr_frame)
                        prec_GT_tag_coutour = prec_contours[prec_ids.index(ST_tag_id)]
                        self.inter_dist = validation.inte_dist(GT_tag_contour, prec_GT_tag_coutour)
                        self.dist = GT_distances[j]
                self.tag_results = next_contours, ids, next_distances, next_rotations
        self.count_curr_frame = (self.count_curr_frame + 1) % self.frame_buffer_size
        return self.tag_results

def signal_handler_stop_running(signal, frame):
    global RUNNING
    RUNNING = False

if __name__ == '__main__':
    """
    Use this script to test the tag recogniotion on raspberry pi.
    """
    RUNNING = True
    # register signals
    #CTRL C
    signal.signal(signal.SIGINT, signal_handler_stop_running)
    tag_detection_experiment = Tag_Detector_Eval() if TRACKING_EVAL else Tag_Detector()
    tag_detection_experiment.start()
    print "CTRL-Z: show image\nCTRL-C shutdown\nallowing camera to warm up"
    time.sleep(2)
    print "let's start!"
    tags_info = None

    # CTRL-C
    while(RUNNING):
        newresults, tags_info = tag_detection_experiment.get_results()
        tags_contours, tags_ids, tags_distances, tags_rotations = tags_info
        if newresults and len(tags_contours)>0:
            
	    message = 'distances: ' + `tags_distances`
            message += '  -  ids: ' + `tags_ids`
	    m2 = "["
	    for id in tags_ids:
	        text = ""
	        if int(id)%4 == 1:
		    id = ((id + (4 - (id%4))) / 4)
		    text = str (id) + "N"
	        elif int(id)%4 == 2:
		    id = ((id + (4 - (id%4))) / 4)
		    text = str (id)+ "E"
	        elif int(id)%4 == 3:
		    id = ((id + (4 - (id%4))) / 4)
		    text = str (id)+ "S"
	        elif int(id)%4 == 0:
		    id = id / 4
		    text = str (id) + "W"
		m2 += text + " "
            m2 += "]"
            message += "  -  orientation: " + m2 + "\n"
            print message
        
        tags_contours, tags_ids, tags_distances, tags_rotations = tags_info
        rgb_image = np.zeros((tag_detection_experiment.prec_frame.shape[0],tag_detection_experiment.prec_frame.shape[1],3),dtype=np.uint8)
        rgb_image[:,:,0] = tag_detection_experiment.prec_frame
        rgb_image[:,:,1] = rgb_image[:,:,0]
        rgb_image[:,:,2] = rgb_image[:,:,0]
        rgb_image = image_utils.draw_contours(rgb_image,tags_contours)
        cv2.imshow('Image', rgb_image)
        key = cv2.waitKey(1) & 0xFF

    cv2.destroyAllWindows()
    tag_detection_experiment.shutdown()
    print "good bye."
