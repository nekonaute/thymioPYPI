import time

import Params
import Simulation

class SimulationDefault(Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.__init__(self, controller, mainLogger)

	def __preActions(self) :
		self.__thymioController.writeMotorsSpeedRequest([300, 300])

	def __step(self) :
		try :
			self.__waitForControllerResponse()
			action = random.randint(0, 5)

			# Go forward
			if action == 0 :
				self.__thymioController.writeMotorsSpeedRequest([300, 300])
			# Turn Left
			elif action == 1 :
				self.__thymioController.writeMotorsSpeedRequest([-300, 300])
				self.__waitForControllerResponse()
				self.__thymioController.writeMotorsSpeedRequest([300, 300])
			# Turn Right
			elif action == 2 :
				self.__thymioController.writeMotorsSpeedRequest([300, -300])
				self.__waitForControllerResponse()
				self.__thymioController.writeMotorsSpeedRequest([300, 300])
			# Go backward
			elif action == 3 :
				self.__thymioController.writeMotorsSpeedRequest([-300, -300])
			# Stop
			elif action == 4 :
				self.__thymioController.writeMotorsSpeedRequest([0, 0])
			# Sound
			elif action == 5 :
				self.__thymioController.writeSoundRequest([440, 1])

			self.__waitForControllerResponse()

			randR = random.randint(0, 32)
			randG = random.randint(0, 32)
			randB = random.randint(0, 32)
			self.__thymioController.writeColorRequest([R, G, B])


			sleepTime = random.randint(0, 5)
			time.sleep(sleepTime)
		except :
			mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
