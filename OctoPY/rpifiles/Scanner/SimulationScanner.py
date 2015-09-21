#!/usr/bin/env/python

import Simulation
import Params

import serial

class SimulationScanner(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__ser = serial.Serial(
															port = Params.params.port,
															baurate = 9600,
															parity = serial.PARITY_NONE,
															stopbits = serial.STOPBITS_ONE,
															bytesize = serial.EIGHTBIYS,
															timeout = 1)


	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		value = self.__ser.readline()
		print(value)