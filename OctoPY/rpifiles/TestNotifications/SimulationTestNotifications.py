#!/usr/bin/env/python

import Simulation
import Params

import time
import random

class SimulationTestNotifications(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		self.mainLogger.debug("INIT !")

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		self.mainLogger.debug("stepou")
		value = random.randint(0, 9)
		self.mainLogger.debug("Random value : " + str(value))
		self.log("Random value : " + str(value))
		self.notify(value = 9)

		sleepTime = random.randint(0, 2)
		self.log("Sleeping : " + str(sleepTime))
		time.sleep(sleepTime)
