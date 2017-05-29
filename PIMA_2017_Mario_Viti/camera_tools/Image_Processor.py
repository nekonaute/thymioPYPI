from Camera_Controller import Camera_Controller
import settings
import threading


class Detector():
    """
    Extend this class to create your detector:

    There are 2 way to do this:

        simple way:
            - in your init function use the super constructor by calling
            Detector.__init__(self)

            - implement the method post_processing_function(self,preprocessing_output)
            preprocessing_output will be an RGB image provided by the camera module
            the RGB image is implemented as a 3D numpy array.

            - the resuts of the return of the post_processing_function will
            be available with a call to the get_results function with a
            prepended boolean newresults.

        different way:
            - define a function preprocessing_function(RGB_image) that takes the as
            argument the RGB image provided by tha camera module and apply a
            preprcessing step and returns a result we'll name preprocessing_output

            - implement the method post_processing_function(self,preprocessing_output)
            preprocessing_output will be the preprocessing_output computed by the user
            defined fucntion preprocessing_function.

    Methods:

        start()
            - starts the camera module and frames stream.

        shutdown()
            - shutdown the camera module and frame stram.

        set_pre_processing_function(preprocessing_function)
            - set the user defined preprocessing_function.

        get_results() -> (newresults, results)
            - result is None: in this case camera couldn't fetch a frame yet so the results
            are not ready.

            - newresults is True: the resuts fetched are computed on a new image.

            - newresults is False: the resuts fetched are old.

        post_processing_function()
            function to be implemented, not implementing this method will raise a
            NotImplementedError.
    """
    def __init__(self):
        self.image_processor = Image_Processor()
        self.image_processor.set_pre_processing_function(self.pre_processing_function)
        self.image_processor.set_post_processing_function(self.post_processing_function)

    def set_pre_processing_function(self,pre_processing_function):
        self.image_processor.set_pre_processing_function(pre_processing_function)

    def pre_processing_function(self,pre_processing_input):
        return pre_processing_input

    def post_processing_function(self,pre_processing_output):
        """
            This method must implement the operations to be applyed to the
            preprocessing output resutls.
        """
        raise NotImplementedError( self.__class__.__name__ + ": should implement post_processing_function(self,preprocessing_output)" )

    def get_results(self):
        newresults, results = self.image_processor.retrieve_post_results()
        return newresults, results

    def start(self):
        self.image_processor.start()

    def shutdown(self):
        self.image_processor.shutdown()

class Image_Processor(threading.Thread):
    def __init__(self):
        super(Image_Processor, self).__init__()
        self.camera_controller = Camera_Controller()
        self.initialize_results()
        self.initialize_locks()
        self.set_pre_processing_function()
        self.set_post_processing_function()

    def initialize_results(self):
        self.new_results_ready = False
        self.new_results_retrived = False

    def initialize_locks(self):
        self.processing_result_lock = threading.Lock()

    def shutdown(self):
        self.running = False
        self.camera_controller.shutdown()

    def set_pre_processing_function(self,pre_processing=lambda x:x):
        self.pre_processing = pre_processing
        self.pre_result = None

    def set_post_processing_function(self,post_processing=lambda x:x):
        self.post_processing = post_processing
        self.post_result = None

    def run(self):
        self.running = True
        self.camera_controller.start()
        self.new_frame = False
        while(self.running):
            with self.camera_controller.processing_buffer_lock:
                if self.camera_controller.processing_buffer != None:
                    self.pre_result = self.pre_processing(self.camera_controller.processing_buffer)
                    self.new_frame = True
            if self.pre_result != None:
                with self.processing_result_lock:
                    if self.new_frame:
                        self.new_frame = False
                        self.post_result = self.post_processing(self.pre_result)
                        self.new_results_ready = True
                        self.new_results_retrived = False
        self.shutdown()

    def retrieve_post_results(self):
        with self.processing_result_lock:
            if self.new_results_retrived:
                self.new_results_ready = False
            self.new_results_retrived = True
            # flag will indicate either results are new or not
            return self.new_results_ready , self.post_result
