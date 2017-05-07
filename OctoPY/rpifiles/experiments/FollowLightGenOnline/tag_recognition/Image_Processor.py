from Camera_Controller import Camera_Controller
import settings
import threading

class Image_Processor(threading.Thread):
    def __init__(self):
        super(Image_Processor, self).__init__()
        self.camera_controller = Camera_Controller()
        self.initialize_results()
        self.initialize_locks()
        self.set_preprocessing_function()
        self.set_post_processing_function()

    def initialize_results(self):
        # jollyfull threading problem reference
        self.available_chop_stick = False
        self.pick_up_chop_stick = False
        self.tag_orientations = None

    def initialize_locks(self):
        self.processing_result_lock = threading.Lock()

    def shutdown(self):
        self.running = False
        self.camera_controller.shutdown()

    def set_preprocessing_function(self,pre_processing=lambda x:x):
        self.pre_processing = pre_processing
        self.pre_result = None

    def set_post_processing_function(self,post_processing=lambda x:x):
        self.post_processing = post_processing
        self.post_result = None

    def run(self):
        self.running = True
        self.camera_controller.start()
        imgray = None
        contours_tag = None
        new_frame = False
        while(self.running):
            with self.camera_controller.processing_buffer_lock:
                if self.camera_controller.processing_buffer != None:
                    self.pre_result = self.pre_processing(self.camera_controller.processing_buffer)
                    new_frame = True
            if self.pre_result != None:
                with self.processing_result_lock:
                    if new_frame:
                        new_frame = False
                        self.post_result = self.post_processing(self.pre_result)
                        self.available_chop_stick = True
                        self.pick_up_chop_stick = False
        self.shutdown()

    def retrieve_post_results(self):
        with self.processing_result_lock:
            if self.pick_up_chop_stick:
                self.available_chop_stick = False
            self.pick_up_chop_stick = True
            # flag will indicate either results are new or not
            return self.available_chop_stick ,self.post_result
