#!/usr/bin/env/python

import sys
import traceback
import logging
from matplotlib import cm
import random
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

class State :
	EXPLORING, FORAGING, DIRECTED, CHARGING = range(0, 4)


class SimulationCollectiveGatheringPlus(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__state = State.EXPLORING
		self.__energy = Params.params.base_energy
		self.__camera = Camera.Camera(mainLogger, COLORS_DETECT)

	def preActions(self) :
		(R, G, B, t) = cm.jet(255)
		self.tController.writeColorRequest([R*32, G*32, B*32])
		self.waitForControllerResponse()

		self.tController.readSensorsRequest()
		self.waitForControllerResponse()

		self.tController.readGroundSensorsRequest()
		self.waitForControllerResponse()

		time.sleep(1)


	def postActions(self) :
		self.tController.writeColorRequest([32, 32, 32])
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
			self.log(str(self.__state))

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
				if self.__state == State.DIRECTED :
					self.tController.readGroundSensorsRequest()
					self.waitForControllerResponse()
					(groundAmbiant, groundReflected, groundDelta) = self.tController.getGroundSensorsValues()

					if groundDelta[0] >= Params.params.white_level :
						if groundDelta[1] >= Params.params.white_level :
							# Black target under the robot
							totalLeft = 0
							totalRight = 0
							self.__state = State.CHARGING
						else :
							# Black target left
							totalLeft = 0
							totalRight = Params.params.base_speed
					else :
						if groundDelta[1] >= Params.params.white_level :
							# Black target right
							totalRight = Params.params.base_speed
							totalRight = 0
						else :
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

							if totalLeft == 0 and totalRight == 0 :
								# The robot moves randomly
								rand = random.random()

								if rand <= 0.5 :
									totalLeft = Params.params.base_speed
									totalRight = 0
								else :
									totalLeft = Params.params.base_speed
									totalRight = Params.params.base_speed
				elif self.__state == State.EXPLORING :
					self.tController.readGroundSensorsRequest()
					self.waitForControllerResponse()
					(groundAmbiant, groundReflected, groundDelta) = self.tController.getGroundSensorsValues()

					# self.log("Ground : " + str(groundDelta[0]) + "/" + str(groundDelta[1]))
					if groundDelta[0] <= Params.params.black_level :
						if groundDelta[1] <= Params.params.black_level :
							# Black target under the robot
							totalLeft = 0
							totalRight = 0
							self.__state = State.FORAGING
						else :
							# Black target left
							totalLeft = 0
							totalRight = Params.params.base_speed
					else :
						if groundDelta[1] <= Params.params.black_level :
							# Black target right
							totalRight = Params.params.base_speed
							totalRight = 0
						else :
							# self.log("Cassos !")
							# self.log("GroundDelta : " + str(groundDelta[0]) + "/" + str(groundDelta[1]))

							# No target spotted, random exploration
							(totalLeft, totalRight) = self.Braitenberg(PSValues)
			else :
				(totalLeft, totalRight) = self.Braitenberg(PSValues)

			self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])


			if self.__state != State.CHARGING :
				self.__energy -= Params.params.energy_decrement

				if self.__energy <= Params.params.energy_threshold :
					self.__state = State.DIRECTED

				if self.__energy <= 0 :
					self.__energy = 0
			else :
				self.__energy += Params.params.energy_increment

				if self.__energy >= Params.params.base_energy :
					self.__state = State.EXPLORING


			(R, G, B, t) = cm.jet(int((self.__energy/float(Params.params.base_energy))*255))
			self.tController.writeColorRequest([R*32, G*32, B*32])
			self.waitForControllerResponse()
		except :
			self.log('SimulationCollectiveGatheringPlus - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
