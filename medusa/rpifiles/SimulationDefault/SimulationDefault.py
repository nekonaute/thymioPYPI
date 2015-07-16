import time
import random

import Params
import Simulation

class SimulationDefault(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

	def preActions(self) :
		pass
		# self.waitForControllerResponse()
		# self.tController.writeMotorsSpeedRequest([300, 300])

	def postActions(self) :
		self.waitForControllerResponse()
		self.tController.writeColorRequest([0, 0, 0])
		self.waitForControllerResponse()


	def step(self) :
		try :
			self.waitForControllerResponse()
			action = random.randint(0, 5)
			action = 6

			# Go forward
			if action == 0 :
				self.tController.writeMotorsSpeedRequest([300, 300])
			# Turn Left
			elif action == 1 :
				self.tController.writeMotorsSpeedRequest([-300, 300])
				self.waitForControllerResponse()
				self.tController.writeMotorsSpeedRequest([300, 300])
			# Turn Right
			elif action == 2 :
				self.tController.writeMotorsSpeedRequest([300, -300])
				self.waitForControllerResponse()
				self.tController.writeMotorsSpeedRequest([300, 300])
			# Go backward
			elif action == 3 :
				self.tController.writeMotorsSpeedRequest([-300, -300])
			# Stop
			elif action == 4 :
				self.tController.writeMotorsSpeedRequest([0, 0])
			# Sound
			elif action == 5 :
				duration = random.randint(1, 2)
				freq = random.randint(200, 600)
				self.tController.writeSoundRequest([freq, duration])

			# self.waitForControllerResponse()

			randR = random.randint(0, 32)
			randG = random.randint(0, 32)
			randB = random.randint(0, 32)
			self.tController.writeColorRequest([randR, randG, randB])


			sleepTime = random.randint(0, 2)
			time.sleep(sleepTime)
		except :
			self.mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
