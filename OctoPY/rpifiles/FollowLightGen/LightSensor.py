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

class LightSensor:
	
	def __init__(self, mainLogger) :
		self.logger = mainLogger
		self.camera = None
	
	def initCam(self):
	      # initialize the camera and grab a reference to the raw camera capture

		self.camera = pc.PiCamera()
		self.camera.resolution = (Params.resolution_X, Params.resolution_Y)
		self.camera.brightness = Params.brightness
			
		#self.camera.start_preview()
		time.sleep(2)
		
	def killCam(self):
		
		#self.camera.stop_preview()
		self.camera.close()
		self.camera=None
		time.sleep(2)
	    
	def lightCaptor(self):
		if self.camera == None:
			self.logger.debug("LightSensor - lightCaptor() : camera non initialisee.")
		else:
			stream = io.BytesIO()
    
			self.camera.capture(stream,format='jpeg')
			
			data = np.fromstring(stream.getvalue(),dtype=np.uint8)
			
			image = cv2.imdecode(data,1)
			image = image[:, :, ::-1]
			

			image_left = image[:,:Params.resolution_X/10*3]
			image_right = image[:,Params.resolution_X/10*7:]
			
			l_left = image_left.mean()
			l_left=l_left/255.0
			l_right = image_right.mean()
			l_right=l_right/255.0
			
			return l_left,l_right
						
			
