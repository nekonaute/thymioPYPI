#!/usr/bin/env/python

import Simulation
import Params

import time
import random
import logging
import sys
import traceback

class SimulationTestNotifications(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		try :
			value = random.randint(0, 9)
			self.log("Random value : " + str(value))
			self.notify(value = value)

			sleepTime = 2
			self.log("Sleeping : " + str(sleepTime), logging.ERROR)
			time.sleep(sleepTime)
		except :
			self.log("SimulationTestNotifications - Unexpected error : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
