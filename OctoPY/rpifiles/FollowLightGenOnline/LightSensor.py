# -*- coding: utf-8 -*-

"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Gestion de la PiCamera pour en faire un capteur de lumière.
"""


import numpy as np
import cv2
import picamera as pc
import time
import io



import Params

from tag_recognition import Image_Processor,image_utils,settings, tag_recognition



class toto():
	
	def __init__(self,mainLogger, tag_settings = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]):
		self.tag_settings = tag_settings
		self.prec_frame = None
		self.image_processor = Image_Processor.Image_Processor()
		self.image_processor.set_preprocessing_function(image_utils.convert_to_HSV)
		self.image_processor.set_post_processing_function(self.post_processing)
		self.mainLogger=mainLogger
								
	def post_processing(self,image):	
		image = image[:, :, 2]

		image_left = image[:,:settings.camera_settings["resolution"][0]/10*3]
		image_right = image[:,settings.camera_settings["resolution"][0]/10*7:]
		
		l_left = image_left.mean()
		l_left=l_left/255.0
		l_right = image_right.mean()
		l_right=l_right/255.0
		
		arear_ratio = self.tag_settings[settings.AREA_RATIO_KEY]
		actual_side_size = self.tag_settings[settings.DIAGONAL_KEY]
		return (l_left+l_right)/2.0, 1 if (l_left > l_right) else 0, tag_recognition.detect_tags(image, arear_ratio, actual_side_size)
		
	def get_light_data(self):
		newresults, light_info = self.image_processor.retrieve_post_results()
		return newresults, light_info

	def start(self):
		self.image_processor.start()
	
	def shutdown(self):
		self.image_processor.shutdown()
	"""
	def __init__(self, tag_settings = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]):
		self.tag_settings = tag_settings
		self.prec_frame = None
		self.tag_results = None
		self.perf_time = None
		self.color_image = None
		self.image_processor = Image_Processor.Image_Processor()
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
	"""

class LightSensor:
	
	def __init__(self, mainLogger) :
		self.logger = mainLogger
		self.camera = None
	
	def initCam(self):
	      # initialize the camera and grab a reference to the raw camera capture

		self.camera = pc.PiCamera()
		self.camera.resolution = (Params.params.resolution_X, Params.params.resolution_Y)
		self.camera.brightness = Params.params.brightness
			
		#self.camera.start_preview()
		time.sleep(2)
		
	def killCam(self):
		
		#self.camera.stop_preview()
		self.camera.close()
		self.camera=None
		time.sleep(2)
	    
	def lightCaptor(self):
		"""
		Retourne le couple (quantité de lumière perçue, 1 si plus de luminosité perçue à gauche qu'à droite 0 sinon).
		"""
		
		if self.camera == None:
			self.logger.debug("LightSensor - lightCaptor() : camera not initialized.")
		else:
			stream = io.BytesIO()
    
			self.camera.capture(stream,format='jpeg')
			
			data = np.fromstring(stream.getvalue(),dtype=np.uint8)
			
			image = cv2.imdecode(data,1)
			image = image[:, :, ::-1]
			

			image_left = image[:,:Params.params.resolution_X/10*3]
			image_right = image[:,Params.params.resolution_X/10*7:]
			
			l_left = image_left.mean()
			l_left=l_left/255.0
			l_right = image_right.mean()
			l_right=l_right/255.0
			
			stream.close()
			
			return (l_left+l_right)/2.0,1 if (l_left > l_right) else 0
