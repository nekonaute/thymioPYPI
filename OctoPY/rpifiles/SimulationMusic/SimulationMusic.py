import time
import random
import re
import os

import Params
import Simulation

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

class SimulationMusic(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__curLine = 0
		if os.path.isfile(os.path.join(CURRENT_FILE_PATH, Params.params.fileSounds)) :
			with open(os.path.join(CURRENT_FILE_PATH, Params.params.fileSounds), 'r') as fileSounds :
				fileSounds = fileSounds.readlines()

				self.__sounds = []
				for line in fileSounds :
					s = re.search(r"^beep -f (\d+\.\d+) -l (\d+\.\d+)$", line.rstrip('\n'))
					if s :
						self.__sounds.append(tuple([float(s.group(1)), float(s.group(2))]))

	def preActions(self) :
		pass

	def postActions(self) :
		self.waitForControllerResponse()
		self.tController.writeColorRequest([0, 0, 0])
		self.waitForControllerResponse()
		self.tController.writeSoundRequest([0, -60])
		self.waitForControllerResponse()

	def step(self) :
		try :
			self.waitForControllerResponse()

			if self.__curLine < len(self.__sounds) :
				self.tController.writeSoundRequest([self.__sounds[self.__curLine][0], self.__sounds[self.__curLine][1]/float(1000)])
			else :
				self.stop()

			self.waitForControllerResponse()

			randR = random.randint(0, 32)
			randG = random.randint(0, 32)
			randB = random.randint(0, 32)
			self.tController.writeColorRequest([randR, randG, randB])

			time.sleep(self.__sounds[self.__curLine][1]/float(1000))
			self.__curLine += 1
		except :
			self.mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
