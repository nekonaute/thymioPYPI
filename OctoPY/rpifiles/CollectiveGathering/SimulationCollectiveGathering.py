#!/usr/bin/env/python

import sys
import traceback

import Simulation
import Params

class SimulationCollectiveGathering(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

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
		totalRight = totalRight + 200
		totalLeft = totalLeft + 200

		return (totalLeft, totalRight)

	def step(self) :
		try :
			self.tController.readGroundSensorsRequest()
			self.waitForControllerResponse()
			(,, groundDelta) = self.tController.getGroundSensorsValues()

			totalLeft = 0
			totalRight = 0
			if groundDelta[0] <= Params.params.black_level :
				if groundDelta[1] <= Params.params.black_level :
					# Black target under the robot
					totalLeft = 300
					totalRight = 300
				else :
					# Black target left
					totalLeft = 0
					totalRight = 300
			else :
				if groundDelta[1] <= Params.params.black_level :
					# Black target right
					totalRight = 300
					totalRight = 0
				else :
					# No target spotted, random exploration
					self.tController.readSensorsRequest()
					self.waitForControllerResponse()
					PSValues = self.tController.getPSValues()
					(totalLeft, totalRight) = self.Braitenberg(PSValues)

			self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])
		except :
			self.log('SimulationCollectiveGathering - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
