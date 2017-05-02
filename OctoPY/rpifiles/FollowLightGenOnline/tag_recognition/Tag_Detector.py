import cv2
import numpy as np
import time

from Image_Processor import Image_Processor
import settings
import tag_recognition
import image_utils
import tests

class Tag_Detector():
    def __init__(self, tag_settings = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]):
        self.tag_settings = tag_settings
        self.prec_frame = None
        self.tag_results = None
        self.perf_time = None
        self.color_image = None
        self.image_processor = Image_Processor()
        self.image_processor.set_preprocessing_function(image_utils.convert_to_HSV)
        self.image_processor.set_post_processing_function(self.post_processing)
        self.count_curr_frame = 0
        self.frame_buffer_size = 3
        self.delta_positions = {}
        self.positions = {}

    def post_processing(self,image):
        arear_ratio = self.tag_settings[settings.AREA_RATIO_KEY]
        actual_side_size = self.tag_settings[settings.DIAGONAL_KEY]
        self.color_image = image #image_utils.threshold_range(image[:,:,0],50,127)
        self.prec_frame = image[:,:,2] # get the v channel
        self.perf_time = time.time()
        self.tag_results = tag_recognition.detect_tags(self.prec_frame ,arear_ratio, actual_side_size=actual_side_size)
        self.perf_time = time.time() - self.perf_time
        return self.tag_results

    def get_tag_data(self):
        newresults, tags_info = self.image_processor.retrieve_post_results()
        return newresults,tags_info

    def start(self):
        self.image_processor.start()

    def shutdown(self):
        self.image_processor.shutdown()
