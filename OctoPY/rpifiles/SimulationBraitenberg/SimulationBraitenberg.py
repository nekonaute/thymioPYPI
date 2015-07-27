import time
import random

import Params
import Simulation

class SimulationBraitenberg(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

	def preActions(self) :
		pass

	def postActions(self) :
		self.waitForControllerResponse()
		self.tController.writeColorRequest([32, 32, 32])
		self.waitForControllerResponse()

	def Braitenberg(self, proxSensors, avoidance = False) :
		self.mainLogger.debug("Avoidance : " + str(avoidance))
		
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
			totalLeft = totalLeft + (proxSensors[i] * leftWheel[i])
			totalRight = totalRight + (proxSensors[i] * rightWheel[i])

		# Add a constant speed
		totalRight = totalRight + 200
		totalLeft = totalLeft + 200

		self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])

		return True

	def step(self) :
		try :
			self.waitForControllerResponse()

			self.tController.readSensorsRequest()
			self.waitForControllerResponse()
			PSValues = self.tController.getPSValues()

			self.Braitenberg(PSValues, bool(Params.params.avoidance))			
		except :
			self.mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

