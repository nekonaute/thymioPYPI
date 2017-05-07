#!/usr/bin/env/python

import Simulation
import Params

import time
import numpy as np
import cv2

from camera_tools import Tag_Detector, tag_recognition
from camera_tools import settings
from camera_tools.tag_recognition import CNT,IDS,DST,ROT


class SimulationFollowTAG(Simulation.Simulation) :
	"""
	Vision experiment, identify nine bit code tags.
	"""
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		# initialize camera controller
		self.image_shape = settings.camera_settings['resolution']
		self.tag_detector = Tag_Detector.Tag_Detector()
		self.distance_tresh = 20

	def preActions(self) :
		# start camera controller
		self.mainLogger.debug('SimulationFollowTAG - starting tag_detector' )
		self.tag_detector.start()

		self.mainLogger.debug('SimulationFollowTAG - camera warm up' )
		time.sleep(3)

	def postActions(self) :
		# shutdown tag_detector
		self.mainLogger.debug('SimulationFollowTAG - camera_controller shutting down' )
		self.tag_detector.shutdown()
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()

	def go_left(self):
		self.mainLogger.debug('SimulationFollowTAG - go_left')
		l_r_motor = [125.0, 250.0]
		self.tController.writeMotorsSpeedRequest(l_r_motor)
		#self.waitForControllerResponse()

	def go_right(self):
		self.mainLogger.debug('SimulationFollowTAG - go_right')
		l_r_motor = [250.0, 125.0]
		self.tController.writeMotorsSpeedRequest(l_r_motor)
		#self.waitForControllerResponse()

	def go_slow(self):
		self.mainLogger.debug('SimulationFollowTAG - stop')
		l_r_motor = [70.0, 70.0]
		self.tController.writeMotorsSpeedRequest(l_r_motor)
		#self.waitForControllerResponse()

	def go_follow(self,cnt):
		M = cv2.moments(cnt)
		cx = int(M['m10']/M['m00'])
		if cx < self.image_shape[0]/2:
			self.go_left()
		else:
			self.go_right()
	
	def go_avoid(self,cnt):
		M = cv2.moments(cnt)
		cx = int(M['m10']/M['m00'])
		if cx < self.image_shape[0]/2:
			self.go_right()
		else:
			self.go_left()

	def step(self) :
		newresults, tags_info = self.tag_detector.get_results()
		if newresults and tags_info != None:
			self.mainLogger.debug('SimulationFollowTAG - tag: ' +  `tags_info[IDS]` )
		if newresults and tags_info != None:
			tag_cnt =  tags_info[CNT]
			tags_ids = tags_info[IDS]
			tag_dist = tags_info[DST]
			if tag_dist != []:
				nearest = np.argmin(np.array(tag_dist))
				cnt = tag_cnt[nearest]
				self.go_follow(cnt)
				self.mainLogger.debug('SimulationFollowTAG - following tag: %d' % tags_ids[nearest] )
		else:
			self.go_slow()
					
	"""
	To set the experiment:
	set config_FollowTAG.cfg
	
	To copy experiments to thymios:
	put ~/thymioPYPI/OctoPY/rpifiles/config_FollowTAG.cfg ~/dev/thymioPYPI/OctoPY/rpifiles	
	put ~/thymioPYPI/OctoPY/rpifiles/FollowTAG ~/dev/thymioPYPI/OctoPY/rpifiles
	
	To update thymios:
	put ~/thymioPYPI/OctoPY/rpifiles/MainController.py ~/dev/thymioPYPI/OctoPY/rpifiles
	put ~/thymioPYPI/OctoPY/rpifiles/Simulation.py ~/dev/thymioPYPI/OctoPY/rpifiles
	put ~/thymioPYPI/OctoPY/rpifiles/ThymioController.py ~/dev/thymioPYPI/OctoPY/rpifiles	
	"""