#!/usr/bin/env/python

import Simulation
import Params
import time

#from raspberry_vision import Tag_Detector

from tag_recognition import Tag_Detector

class SimulationFollowTAG(Simulation.Simulation) :
	"""
	Vision experiment, identify nine bit code tags.
	"""
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		# initialize camera controller
		#self.tag_detector = Tag_Detector.Tag_Detector()
		self.tag_detector = Tag_Detector.Tag_detection_experiment()

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
		#go_left = [125.0, 215.1]
		#go_right = [215.1, 125.0]

		#newresults, orientation = self.tag_detector.retrieve_tag_orientations()
		newresults, tags_info = self.tag_detector.retrieve_post_results()
        	tags_contours,tags_aligned,tags_ids,tags_distances,tags_rotations = tags_info
		if tags_ids!=[] and newresults:
			for i in xrange(len(tags_ids)):
				self.mainLogger.debug('SimulationFollowTAG - tag id: %d' % tags_ids[i] )
				self.mainLogger.debug('SimulationFollowTAG - tag id: %d' % tags_ids[i] )
				self.mainLogger.debug('SimulationFollowTAG - tag id: %d' % tags_ids[i] )		
			#if tags_rotations[0] > 0:
				#self.mainLogger.debug('SimulationFollowTAG - saw a triangle pointing left' )
				#self.tController.writeMotorsSpeedRequest(go_left)
			#else:
				#self.mainLogger.debug('SimulationFollowTAG - saw a triangle pointing right' )
				#self.tController.writeMotorsSpeedRequest(go_right)
		
