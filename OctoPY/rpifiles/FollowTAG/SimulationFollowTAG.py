#!/usr/bin/env/python

import Simulation
import Params
import time

from raspberry_vision import Tag_Detector

class SimulationFollowTAG(Simulation.Simulation) :
	"""
	Vision experiment, follow a triangle direction.
	Tags are equilateral triangles pointing either left or right.
	"""
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		# initialize camera controller
		self.tag_detector = Tag_Detector.Tag_Detector()

	def preActions(self) :
		# start camera controller
		self.mainLogger.debug('SimulationFollowTAG - starting tag_detector' )
		self.tag_detector.start()
		self.mainLogger.debug('SimulationFollowTAG - camera warm up' )
		time.sleep(3)

	def postActions(self) :
		# shutdown tag_detector
		self.tag_detector.shutdown()
		self.mainLogger.debug('SimulationFollowTAG - camera_controller shutting down' )
		self.tController.writeMotorsSpeedRequest([0, 0])

	def step(self) :
		go_left = [25.0, 215.1]
		go_right = [215.1, 25.0]

		newresults, orientation = self.tag_detector.retrieve_tag_orientations()
		if orientation!=[] and newresults:
			if orientation[0] == 0:
				#self.mainLogger.debug('SimulationFollowTAG - saw a triangle pointing left' )
				self.tController.writeMotorsSpeedRequest(go_left)
			else:
				#self.mainLogger.debug('SimulationFollowTAG - saw a triangle pointing right' )
				self.tController.writeMotorsSpeedRequest(go_right)
		
