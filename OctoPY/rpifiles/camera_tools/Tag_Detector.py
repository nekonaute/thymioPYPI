import cv2
import numpy as np
import time

from Image_Processor import Detector
import settings
from tag_recognition import CNT,IDS,DST,ROT
import tag_recognition
import image_utils
import tests

class Tag_Detector(Detector):
    def __init__(self, tag_settings = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]):
        Detector.__init__(self)
        self.tag_settings = tag_settings
        self.prec_frame = None
        self.tag_results = None
        self.perf_time = None
        self.color_image = None
        self.set_preprocessing_function(image_utils.convert_to_HSV)
        self.count_curr_frame = 0
        self.frame_buffer_size = 2
        self.delta_positions = {}
        self.positions = {}

    def post_processing_function(self,image):
        arear_ratio = self.tag_settings[settings.AREA_RATIO_KEY]
        actual_side_size = self.tag_settings[settings.DIAGONAL_KEY]
        self.perf_time = time.time()
        if self.count_curr_frame == 0:
            self.prec_frame = image[:,:,2]
            self.tag_results = tag_recognition.detect_tags(self.prec_frame ,arear_ratio, actual_side_size=actual_side_size)
        elif self.count_curr_frame == 1:
            prec_contours = self.tag_results[CNT]
            prec_frame = self.prec_frame
            curr_frame = image[:,:,2]
            if len(prec_contours)>0:
                status, next_contours, next_distances, next_rotations = tag_recognition.estimate_next_positions(prec_frame,curr_frame,prec_contours)
                ids = np.array(self.tag_results[IDS])[status==1]
                self.tag_results = next_contours, ids, next_distances, next_rotations
        self.count_curr_frame = (self.count_curr_frame + 1) % self.frame_buffer_size
        self.perf_time = time.time() - self.perf_time
        return self.tag_results
