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

from tools.camera_tools.Image_Processor import Detector

class LightAndTagSensor(Detector):
	def __init__(self,mainLogger):
		Detector.__init__(self);
		
		self.mainLogger=mainLogger
								
	def post_processing_function(self,image):	
		image = image[:, :, 2]
		
		image_width = len(image[0])

		image_left = image[:,:image_width/10*3]
		image_right = image[:,image_width/10*7:]
		
		l_left = image_left.mean()
		l_left=l_left/255.0
		l_right = image_right.mean()
		l_right=l_right/255.0
	
		return (l_left+l_right)/2.0, 1 if (l_left > l_right) else 0
		
	def get_light_data(self):
		newresults, light_info = self.get_results()
		return newresults, light_info

"""
Utilisation de la caméra pour en faire un capteur de lumière.
DEPRECATED : non efficace, utiliser camera_tools disponible dans thymioPYPI/OctoPY/rpifiles/tools.
"""
class Light_sensor:
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