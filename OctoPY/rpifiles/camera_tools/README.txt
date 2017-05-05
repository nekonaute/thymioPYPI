Process camera frames

HOWTO:

from camera_tools import Image_Processor.Detector

Extend the Image_Processor.Detector class to create your detector:
The Tag_Detector class is given as an example of implementation.

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

      set_preprocessing_function(preprocessing_function)
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
