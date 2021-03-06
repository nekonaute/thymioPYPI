import threading
import traceback
import logging
import sys
from abc import ABCMeta, abstractmethod

import ThymioController
import Params


"""
OCTOPY : Simulation.py

Basic model for any simulation : every simulation will automatically inherit from 
this class when created by CreateExperiment.py.
N.B : takes care of launching "its" ThymioController.
"""

class Simulation(threading.Thread) :
	__metaclass__ = ABCMeta

	# Compulsory parameters
	compParams = ['simulation_name', 'simulation_path']

	def __init__(self, controller, mainLogger, debug = False) :
		threading.Thread.__init__(self)

		self.daemon = True

		# Main controller
		self.controller = controller

		self.__stop = threading.Event()
		self.__pause = threading.Event()
		self.__restart = threading.Event()

		self.__data = []

		# Thymio controller
		if not debug :
			self.__tcPA = False
			self.__tcPerformedAction = threading.Condition()			
			
			self.tController = ThymioController.ThymioController(self, mainLogger) 
			self.tController.start()

		self.mainLogger = mainLogger

	def run(self) :
		try :
			self.preActions()

			while not self.__stop.isSet() :
				self.step()

				if self.__pause.isSet() :
					self.pauseActions()

					while not self.__restart.isSet() :
						self.__restart.wait()

			self.postActions()
			
			self.tController.stop()
			self.tController.join()
			
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
			self.postActions()
			self.tController.stop()
			self.tController.join()

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	@abstractmethod
	def step(self) :
		pass

	def addData(self, data) :
		self.__data.append(data)

	def getData(self) :
		if len(self.__data) > 0 :
			return self.__data.pop(0)
		else :
			return None

	def dataSize(self) :
		return len(self.__data)

	def receiveComMessage(self, data) :
		pass

	def log(self, message, level = logging.DEBUG) :
		self.mainLogger.log(level, message)

	def pause(self) :
		self.__pause.set()
		self.__restart.clear()

	def pauseActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])

	def restart(self) :
		self.__restart.set()
		self.__pause.clear()

	def isPaused(self) :
		return self.__pause.isSet()

	def stop(self) :
		self.__stop.set()

	def isStopped(self) :
		return self.__stop.isSet()

	def reset(self) :
		pass
		
	def thymioControllerPerformedAction(self) :
		with self.__tcPerformedAction:
			self.__tcPA = True
			self.__tcPerformedAction.notify()

	def waitForControllerResponse(self) :
		# Wait for ThymioController response
		with self.__tcPerformedAction :
			while not self.__tcPA and not self.__stop.isSet() :
				self.__tcPerformedAction.wait()
			# self.mainLogger.debug("WAIT ENDED")
			self.__tcPA = False
	
	def startThymioController(self) :
		self.tController.start()

	def stopThymioController(self) :
		self.tController.stop()

	def notify(self, **params) :
		self.mainLogger.debug("Simulation - Notifying with : " + str(params))
		self.controller.notify(**params)

	def sendMessage(self, **params) :
		self.mainLogger.debug("Simulation - Sending message with : " + str(params))
		self.controller.sendMessage(**params)

	# --- Functions for easy thymio movement ---
	def turn(self, angle) :
		try :
			self.tController.readMotorsSpeedRequest()
			self.waitForControllerResponse()

			motorsSpeed = self.tController.getMotorSpeed()

			angularSpeed = (angle * 32.0)/9.0

			if angle < 1 and angle > -1 :
				#m = np.max(motorsSpeed)
				self.tController.writeMotorsSpeedRequest(motorsSpeed)
				self.waitForControllerResponse()

			if angle > 0 :
				self.tController.writeMotorsSpeedRequest([angularSpeed + motorsSpeed[0], motorsSpeed[1] - angularSpeed])
			else :
				angularSpeed = angularSpeed * -1.0
				self.tController.writeMotorsSpeedRequest([motorsSpeed[0] - angularSpeed, motorsSpeed[1] + angularSpeed])

			self.waitForControllerResponse()
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

	def move(self, angle, speedLeft, speedRight) :
		try :
			self.tController.writeMotorsSpeedRequest([speedLeft, speedRight])
			self.waitForControllerResponse()

			angularSpeed = (angle * 32.0)/9.0

			if angle < 1 and angle > -1 :
				self.tController.writeMotorsSpeedRequest([speedLeft, speedRight])
				self.waitForControllerResponse()
				return

			if angle > 0 :
				self.tController.writeMotorsSpeedRequest([speedLeft + angularSpeed, speedRight - angularSpeed])
			else :
				angularSpeed = angularSpeed * -1.0
				self.tController.writeMotorsSpeedRequest([speedLeft - angularSpeed, speedRight + angularSpeed])

			self.waitForControllerResponse()
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())


	def move2(self, angle, area, minSize, maxSize, speedLeft, speedRight) :
		try :
			if area > maxSize :
				self.tController.writeMotorsSpeedRequest([0, 0])
				return

			if area < minSize :
				self.tController.writeMotorsSpeedRequest([0, 0])
				return

			self.move(angle, speedLeft, speedRight)
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())


	@staticmethod
	def checkForCompParams() :
		for param in Simulation.compParams :
			if not Params.params.checkParam(param) :
				#self.mainLogger.error("Simulation - Parameter " + param + " not found.")
				return False

		return True