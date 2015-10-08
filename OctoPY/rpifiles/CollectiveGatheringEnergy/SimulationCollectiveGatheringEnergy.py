#!/usr/bin/env/python

import sys
import traceback
import logging
from matplotlib import cm

import Simulation
import Params

class State :
	EXPLORING, FORAGING, DIRECTED, CHARGING = range(0, 4)


class SimulationCollectiveGatheringEnergy(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__state = State.EXPLORING
		self.__energy = Params.params.base_energy

	def preActions(self) :
		(R, G, B, t) = cm.jet(255)
		self.tController.writeColorRequest([R*32, G*32, B*32])
		self.waitForControllerResponse()

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
				if self.__state == State.EXPLORING :
					(totalLeft, totalRight) = self.Braitenberg(PSValues)
				elif self.__state == State.FORAGING :
					self.tController.readGroundSensorsRequest()
					self.waitForControllerResponse()
					(groundAmbiant, groundReflected, groundDelta) = self.tController.getGroundSensorsValues()

					# self.log("Ground : " + str(groundDelta[0]) + "/" + str(groundDelta[1]))
					if groundDelta[0] <= Params.params.black_level :
						if groundDelta[1] <= Params.params.black_level :
							# Black target under the robot
							totalLeft = 0
							totalRight = 0
							self.__state = State.CHARGING
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
							# No target spotted, random exploration
							(totalLeft, totalRight) = self.Braitenberg(PSValues)
			else :
				(totalLeft, totalRight) = self.Braitenberg(PSValues)

			self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])

			if self.__state == State.EXPLORING or self.__state == State.FORAGING :
				self.__energy -= Params.params.energy_decrement
			elif self.__state == State.CHARGING :
				self.__energy += Params.params.energy_increment

			if self.__energy <= Params.params.energy_threshold and self.__state == State.EXPLORING :
				self.__state = State.FORAGING

			if self.__energy >= Params.params.base_energy and self.__state == State.CHARGING :
				self.__state = State.EXPLORING

			(R, G, B, t) = cm.jet(int((self.__energy/float(Params.params.base_energy))*255))
			self.tController.writeColorRequest([R*32, G*32, B*32])
			self.waitForControllerResponse()
		except :
			self.log('SimulationCollectiveGathering - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
