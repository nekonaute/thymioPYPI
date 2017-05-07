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

class RaspbClass():
	def __init__(self,thy_controller,demo=False,saving=False):
		self.expect =  []
		self.thymio = thy_controller
		self._stop = False
		self.demo = demo or tools.DEMO
		self.save = saving or tools.SAVING
		self.daemon = True
		self.diff_tagz = False
		#tools.IEME_TAG = 0
		self.initCam()
		
	def initCam(self):
		# initialize the camera and grab a reference to the raw camera capture
		self.camera = PiCamera()
		self.camera.resolution = (tools.SIZE_X, tools.SIZE_Y)
		#camera.framerate = 64
		self.camera.brightness = tools.INIT_BRIGHTNESS
		self.rawCapture = PiRGBArray(self.camera, size=(tools.SIZE_X, tools.SIZE_Y))
		print "Initializing camera"
		# allow the camera to warmup
		time.sleep(3)

	def tag_expected(self,tagz):
		self.diff_tagz = True
		print "Will expect to find these tags :",tagz
		self.expected = tagz
	
	def bot_expected(self,bots):
		self.diff_tagz = False
		print "Will expect to find these robots :",bots
		self.expected = bots
		
	def set_demo(self,is_demo):
		self.demo = is_demo
	
	def set_saving(self,is_save):
		self.save = is_save
		
	def add_expected(self,robot):
		self.expected.append(robot)
	
	def verify_results(self, results):
		"""
		Verifying the robots found in the image area
		if their id and direction match
		"""
		found_ok = 0
		mistakes = 0
		for bot in results:
			if not self.diff_tagz:
				info = bot[0]
			else:
				info = (bot[0],bot[1])
			if info in self.expected:
				found_ok += 1
			else :
				mistakes += 1
		return found_ok, mistakes
		
	def start(self):
		# if we wan to run a demonstration of the robot capacities
		self.run()
			
	def run(self):
		ststr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%Hh%Mmin')
		self.log = "\n Prise du {}\n".format(ststr)
		self.log += "\n***Récupération des données de l'arène***"
		self.log += "\n\tInitial brightness = {}".format(self.camera.brightness)
		self.log += "\n\tCamera asked framerate = {}".format(self.camera.framerate)
		self.log += "\n\tCamera resolution = {}".format(self.camera.resolution)
		self.log += "Will expect to find these tags : {}".format(self.expected)
		self.log_writer = io.WriteLog(self.log)
		self.log_writer.start()
		print "Raspberry in process"
		i = 0
		nbImgSec = 0
		st = dt = d_dur = time.time()
		print "\nStarting vizualization!"
		for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
			self.log = ""
			self.thymio.light_off()
			# stopping any noise
			if self._stop:
				tools.BRIGHT_PLOT_TIME = time.time()-d_dur
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
				self.camera.brightness += verif            
				self.log += "\n****** Brightness changed : {} ******\n".format(self.camera.brightness)
			# tests sur l'image
			results = tg.found_tag_img(image, demo = self.demo, save=self.save)
			print "\nTemps = "+str(time.time() - dt)
			self.log += "\nTemps = {}".format(time.time() - dt)
			# writing if there was or not any tag in the image
			if results==[]:
				print "|---> No tag found"
				self.log += "\n|---> No tag found"
				tools.NEGS+=1
			else:
				found, mis  = self.verify_results(results)
				tools.FALSE_POS+=mis
				tools.TRUE_POS+=found
				if found == 0 :
					print "|---> WRONG (0 good) -> Robot seen : ",results
					self.log += "\n|---> WRONG (0 good) -> Robot seen : {}".format(results)
					self.thymio.found_wrong()
				elif mis==0:
					print "|---> ALLGOOD (0 wrong) -> Robot seen : ",results
					self.log += "\n|---> GOOD -> Robot seen : {}".format(results)
					self.thymio.found_good()
				else:
					print "|---> GOOD ({} good - {} wrong) -> Robot seen : {}".format(found,mis,results)
					self.log += "\n|---> GOOD ({} good - {} wrong) -> Robot seen : {}".format(found,mis,results)
					self.thymio.found_half()
			self.rawCapture.truncate(0)
			dt = time.time()
			if(dt-st-0.1>=1):
				print "\n1 seconde ecoulee : {} images prises".format(nbImgSec)
				self.log += "\n1 seconde ecoulee : {} images prises".format(nbImgSec)
				st=dt
				nbImgSec = 0
			self.log_writer.nextString(self.log)
			if self.demo:
				key = cv2.waitKey(1) & 0xFF
				# not working : cv2 not showing
				# if the `q` key was pressed, break from the loop
				if key == ord("q") :
					cv2.destroyAllWindows()	
					self._stop = True
		# end for
		
	def stopping(self):
		self._stop = True
		print "\nEnd vizualization"
		io.writeOutputFile(self.log,log=True)
		if self.demo:
			cv2.destroyAllWindows()	
		self.thymio.stopping()
		self.log_writer.stopping()
		self.log_writer.join()

