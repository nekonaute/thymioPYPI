from Camera_Controller import Camera_Controller
import settings
import tag_recognition
import threading

class Tag_Detector(threading.Thread):
    def __init__(self, tag_settings = settings.tag_settings):
        super(Tag_Detector, self).__init__()
        self.camera_controller = Camera_Controller()
        self.load_tag_settings(tag_settings)
        self.initialize_results()
        self.initialize_locks()

    def load_tag_settings(self,tag_settings):
        self.tag_area_ratio = tag_settings['area_ratio']

    def initialize_results(self):
        # jollyfull threading problem reference
        self.available_chop_stick = True
        self.retrieve_chop_stick = False
        self.tag_orientations = None

    def initialize_locks(self):
        self.processing_result_lock = threading.Lock()

    def shutdown(self):
        self.running = False
        self.camera_controller.shutdown()

    def run(self):
        self.running = True
        self.camera_controller.start()
        while(self.running):
            imgray = None
            with self.camera_controller.processing_buffer_lock:
                if self.camera_controller.processing_buffer != None:
                    imgray = tag_recognition.pre_processing_image(self.camera_controller.processing_buffer)
            if imgray!= None:
                contours_tag, tag_ids = tag_recognition.detecting_tag(imgray,self.tag_area_ratio)
                extsLeft,extsRight,extsTop,extsBottom = tag_recognition.countours_extreme_points(contours_tag)
                with self.processing_result_lock:
                    self.tag_orientations = []
                    for i in range(len(extsLeft)):
                        ori = tag_recognition.triangle_orientation(extsLeft[i],extsRight[i],extsTop[i],extsBottom[i])
                        self.tag_orientations += [ori]
                    self.available_chop_stick = True
                    self.pick_up_chop_stick = False
        self.shutdown()

    def retrieve_tag_orientations(self):
        with self.processing_result_lock:
            if self.pick_up_chop_stick:
                self.available_chop_stick = False
            self.pick_up_chop_stick = True
            return self.available_chop_stick ,self.tag_orientations
