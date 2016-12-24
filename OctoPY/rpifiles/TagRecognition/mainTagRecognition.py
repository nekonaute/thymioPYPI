#!/usr/bin/env python

import numpy as np
import cv2
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import datetime
import gobject

import tools
import found_tag_box as tg


class MainTagRecognition :
	def __init__(self, mainLogger) :
		self.initCam(self)
		self.nbImgSec = 0
		self.cpt = 0
		
	def initCam(self):
		# initialize the camera and grab a reference to the raw camera capture
		self.camera = PiCamera()
		self.camera.resolution = (tools.SIZE_X, tools.SIZE_Y)
		#camera.framerate = 64
		self.camera.brightness = tools.INIT_BRIGHTNESS
		self.rawCapture = PiRGBArray(self.camera, size=(tools.SIZE_X, tools.SIZE_Y))

		# allow the camera to warmup
		time.sleep(3)

	def searchTags(self) :
		frame = self.camera.capture(self.rawCapture, format="bgr", use_video_port=True):

		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image = frame.array
		self.nbImgSec += 1
		self.cpt += 1
		verif = 0
		if self.cpt%tools.BRIGHTNESS_CHECK!=0:
			verif = tools.verify_brightness(image)
		else:
			verif = tools.verify_brightness(image,go=True)

		# there was a modification
		if verif!=0:
			self.camera.brightness += verif            
			self.log("****** Brightness changed : {} ******".format(self.camera.brightness))

		# tests on image
		# Return the list of tuples with 
		# (robot's number, robot's orientation string, robot's orientation angle, robot's distance, robot's direction from me)
		results = tg.found_tag_img(image, demo = self.demo, save=self.save)

		return results