#!/usr/bin/env/python

import Simulation
import Params

class SimulationTest(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		pass