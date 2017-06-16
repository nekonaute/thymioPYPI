import time
import random
import sys

import Params
import Simulation

PROX_SENSORS_MAX_VALUE = 4500

class SimulationBraitenberg(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		if Params.params.avoidance == "False" :
			self.__avoidance = False
		else :
			self.__avoidance = True

		self.__probaTurn = float(Params.params.probaTurn)

	def preActions(self) :
		pass

	def postActions(self) :
		self.waitForControllerResponse()
		self.tController.writeColorRequest([32, 32, 32])
		self.waitForControllerResponse()
		self.tController.writeMotorsSpeedRequest([0, 0])

	def Braitenberg(self, proxSensors, avoidance) :
		if not avoidance :
			leftWheel = [-0.1, -0.05, -0.001, 0.06, 0.15]
			rightWheel = [0.12, 0.07, -0.002, -0.055, -0.11]
		else :
			leftWheel = [0.1, 0.05, 0.001, -0.06, -0.15]
			rightWheel = [-0.12, -0.07, 0.002, 0.055, 0.11]

		# Braitenberg algorithm
		totalLeft = 0
		totalRight = 0
		for i in range(5) :
			if not avoidance :
				value = 0.0

				if proxSensors[i] > 0.0 :
					value = PROX_SENSORS_MAX_VALUE - proxSensors[i]

					if value < 0.0 :
						value = 0.0

				# self.log(str(i) + "/" + str(proxSensors[i]) + "/" + str(value))
				totalLeft = totalLeft + (value * leftWheel[i])
				totalRight = totalRight + (value * rightWheel[i])
			else :
				totalLeft = totalLeft + (proxSensors[i] * leftWheel[i])
				totalRight = totalRight + (proxSensors[i] * rightWheel[i])

		# Add a constant speed
		# if not avoidance :
		# 	totalRight = totalRight + 150
		# 	totalLeft = totalLeft + 150
		# else :
		totalRight = totalRight + 200
		totalLeft = totalLeft + 200

		self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])

		return True

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

			if noObstacle :
				# Probability to do a left a right turn
				rand = random.random()

				if rand < self.__probaTurn :
					rand = random.random()

					if rand < 0.5 :
						self.tController.writeMotorsSpeedRequest([200, 0])
					else :
						self.tController.writeMotorsSpeedRequest([0, 200])
					self.waitForControllerResponse()
					time.sleep(0.5)

				self.tController.writeMotorsSpeedRequest([200, 200])
			else :
				self.Braitenberg(PSValues, self.__avoidance)
		except :
			self.mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

