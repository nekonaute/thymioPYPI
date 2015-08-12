#!/usr/bin/env/python

import Simulation
import Params

import time
import random

class SimulationTestNotifications(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		value = random.randint(0, 9)
		log("Random value : " + value)
		self.notify(value = 9)

		sleepTime = random.randint(0, 2)
		log("Sleeping : " + sleepTime)
		time.sleep(sleepTime)
