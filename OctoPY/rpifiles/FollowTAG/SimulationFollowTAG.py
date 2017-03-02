#!/usr/bin/env/python

import Simulation
import Params

class SimulationFollowTAG(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

	def preActions(self) :
		pass

	def postActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])

	def step(self) :
		print 'Hello stdout'
		pass
