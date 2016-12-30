# -*- coding: utf-8 -*-
import numpy as np
import cv2
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import datetime
import gobject
# from our files
import tools
import found_tag_box as tg
import gestIO as io
import generePlots as plt

STOP = False

def initCam():
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (tools.SIZE_X, tools.SIZE_Y)
    #camera.framerate = 64
    camera.brightness = tools.INIT_BRIGHTNESS
    rawCapture = PiRGBArray(camera, size=(tools.SIZE_X, tools.SIZE_Y))
    print "Initializing camera"
    # allow the camera to warmup
    time.sleep(3)
    return camera,rawCapture

def run(thymio, expected = [], demo = False):
	STOP = False
	print "Raspberry in process"
	i = 0
	nbImgSec = 0
	camera,rawCapture = initCam()
	st = dt = time.time()
	print "\nStarting vizualization!"
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		if STOP:
			break
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image = frame.array
		nbImgSec += 1
		i += 1
		if i%tools.BRIGHTNESS_CHECK!=0:
			verif = tools.verify_brightness(image)
		else:
			verif = tools.verify_brightness(image,go=True)
		# there were a modification
		if verif!=0:
			camera.brightness += verif            
			print "Brightness",camera.brightness
		# tests sur l'image
		results = tg.found_tag_img(image, demo = demo)
		print "\nTemps = "+str(time.time() - dt)
		# writing if there was or not any tag in the image
		if results==[]:
			print " ---> No tag found"
		elif any([x in expected for x in results]):
			#self.thy_controller.found_good()
			print "GOOD -> Robot seen : ",results
		else:
			#self.thy_controller.found_wrong()
			print "WRONG -> Robot seen : ",results
		# show the frame
		key = cv2.waitKey(1) & 0xFF
		rawCapture.truncate(0)
		# not working : cv2 not showing
		# if the `q` key was pressed, break from the loop
		if key == ord("q") :#or i>=tools.ITERATIONS:
			STOP = True
			break
		dt = time.time()
		"""
		if(dt-st>=1):
		#print "\n1seconde ecoulee : {} images prises".format(nbImgSec)
		st=ft
		nbImgSec = 0
		"""
	# end with
	print "\nEnd vizualization"
	# When everything's done, release the capture
	#camera.stop_preview()
	cv2.destroyAllWindows()
	
def stopping():
    STOP = True
