#!/usr/bin/env/python

import logging
import time
import sys
import traceback
import numpy as np
import time

import Simulation
import Params
import Camera

# Colors detection information
COLORS_DETECT = {
									# "purple" : { 
									# 					"min" : np.array([40, 40, 40]),
									# 					"max" : np.array([80, 255, 255]),
									# 					"input1" : 1,
									# 					"input2" : 0,
									# 					"input3" : 0
									# 				},
									"red" : { 
														"min" : np.array([160, 50, 50]),
														"max" : np.array([180, 255, 255])
													},
									"red2" : { 
														"min" : np.array([0, 50, 50]),
														"max" : np.array([20, 255, 255])
													},
									# "green" : { 
									# 					"min" : np.array([40, 40, 40]),
									# 					"max" : np.array([80, 255, 255]),
									# 					"input1" : 0,
									# 					"input2" : 1,
									# 					"input3" : 0
									# 				},
								}


class SimulationFollowColor(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__camera = Camera.Camera(mainLogger, COLORS_DETECT)


	def preActions(self) :
		pass

	def postActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])


	def Braitenberg(self, proxSensors) :
		leftWheel = [0.1, 0.05, 0.001, -0.06, -0.15]
		rightWheel = [-0.12, -0.07, 0.002, 0.055, 0.11]

		# Braitenberg algorithm
		totalLeft = 0
		totalRight = 0
		for i in range(5) :
			totalLeft = totalLeft + (proxSensors[i] * leftWheel[i])
			totalRight = totalRight + (proxSensors[i] * rightWheel[i])

		# Add a constant speed
		totalRight = totalRight + Params.params.base_speed
		totalLeft = totalLeft + Params.params.base_speed

		return (totalLeft, totalRight)


	def step(self) :
		try :
			self.waitForControllerResponse()

			self.tController.readSensorsRequest()
			self.waitForControllerResponse()
			PSValues = self.tController.getPSValues()

			noObstacle = True
			for i in range(5) :
				if PSValues[i] > 0 :
					noObstacle = False
					break

			totalLeft = 0
			totalRight = 0
			if noObstacle :
				leftWheel = [-0.25, -0.2, -0.15, -0.1, -0.05, -0.01, 0.01, 0.05, 0.1, 0.15, 0.2, 0.25]
				rightWheel = [0.25, 0.2, 0.15, 0.1, 0.05, 0.01, -0.01, -0.05, -0.1, -0.15, -0.2, -0.25]

				listDetect = self.__camera.detectColors()

				assert(len(listDetect) >= Params.params.nb_rays)
				for i in range(0, Params.params.nb_rays) :
					colorDetected = listDetect[i]

					# self.log("Ray " + str(i) + " : " + colorDetected)
					if colorDetected != 'none' :
						totalLeft += leftWheel[i] * Params.params.base_speed
						totalRight += rightWheel[i] * Params.params.base_speed

				totalLeft += Params.params.default_speed
				totalRight += Params.params.default_speed
			else :
				(totalLeft, totalRight) = self.Braitenberg(PSValues)

			self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])

			time.sleep(Params.params.time_step/1000.0)
		except :
			self.log('SimulationStagHunt - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
