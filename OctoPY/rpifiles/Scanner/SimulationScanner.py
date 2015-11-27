#!/usr/bin/env/python

import Simulation
import Params

import serial
import sys
import traceback
import threading
import time
import random
import logging
import os

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

class SerialReader(threading.Thread) :
	def __init__(self, mainLogger, simulation) :
		threading.Thread.__init__(self)
		self.__mainLogger = mainLogger
		self.__simulation = simulation

		self.daemon = True
		self.__stop = threading.Event()

		self.__ser = serial.Serial(
															port = Params.params.port,
															baudrate = 9600,
															parity = serial.PARITY_NONE,
															stopbits = serial.STOPBITS_ONE,
															bytesize = serial.EIGHTBITS,
															timeout = 1)

		self.__nbRead = 0


	def run(self) :
		self.__mainLogger.debug('SerialReader - Running SerialReader.')
		while not self.__stop.isSet() :
			try :
				value = self.__ser.readline()
				if len(value) > 0 :
					self.__mainLogger.debug('SerialReader - Adding ' + value + ' to buffer.')
					self.__simulation.addToBuffer(value.rstrip('\n'))
					self.__nbRead += 1

				time.sleep(1/10)
			except :
				self.__mainLogger.critical('SerialReader - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

	def getNbRead(self) :
		return self.__nbRead

	def stop(self) :
		self.__stop.set()


class SimulationScanner(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__reader = SerialReader(mainLogger, self)

		self.__buff = []

		if Params.params.avoidance == "False" :
			self.__avoidance = False
		else :
			self.__avoidance = True

		# Creation of the logging handlers
		self.__scanLogger = logging.getLogger('scanner')
		self.__scanLogger.setLevel(logging.DEBUG)

		log_path = os.path.join(CURRENT_FILE_PATH, 'scan.log')
		fileHandler = logging.FileHandler(log_path)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
		fileHandler.setFormatter(formatter)
		fileHandler.setLevel(logging.DEBUG)
		self.__scanLogger.addHandler(fileHandler)

	def preActions(self) :
		self.__reader.start()

	def postActions(self) :
		self.__reader.stop()
		self.tController.writeMotorsSpeedRequest([0, 0])

	def addToBuffer(self, value) :
		self.__buff.append(value)

	def readBuffer(self) :
		if len(self.__buff) > 0:
			return self.__buff.pop(0)
		else :
			return None


	def Braitenberg(self, proxSensors, avoidance) :
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
			self.tController.readSensorsRequest()
			self.waitForControllerResponse()
			PSValues = self.tController.getPSValues()

			noObstacle = True
			for i in range(5) :
				if PSValues[i] > 0 :
					noObstacle = False
					break

			if noObstacle :
				# Probability to do a left or right turn
				rand = random.random()

				if rand < 0.001 :
					rand = random.random()

					if rand < 0.5 :
						self.tController.writeMotorsSpeedRequest([200, 0])
					else :
						self.tController.writeMotorsSpeedRequest([0, 200])
					self.waitForControllerResponse()
					time.sleep(0.5)

				self.tController.writeMotorsSpeedRequest([200, 200])
			else :
				self.Braitenberg(PSValues, self.__avoidance)

			value = self.readBuffer()
			if value != None :
				self.__scanLogger.debug('Value : ' + value)

			time.sleep(0.01)
		except :
			self.mainLogger.critical('SimulationScanner - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())