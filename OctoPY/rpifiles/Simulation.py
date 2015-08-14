import threading
import traceback
import logging
import sys

from abc import ABCMeta, abstractmethod

import numpy as np

import ThymioController
import Params


class Simulation(threading.Thread) :
	__metaclass__ = ABCMeta

	# Compulsory parameters
	compParams = ['simulation_name', 'simulation_path']

	def __init__(self, controller, mainLogger) :
		threading.Thread.__init__(self)

		self.daemon = True

		# Main controller
		self.controller = controller

		self.__stop = threading.Event()
		self.__pause = threading.Event()
		self.__restart = threading.Event()

		# Thymio controller
		self.__tcPA = False
		self.__tcPerformedAction = threading.Condition()
		self.tController = ThymioController.ThymioController(self, mainLogger) 
		self.tController.start()

		self.mainLogger = mainLogger

	def run(self) :
		self.mainLogger.debug("Simulation - Start")
		self.preActions()

		self.mainLogger.debug("Simulation - GO GO GO")
		while not self.__stop.isSet() :
			self.mainLogger.debug("Simulation - Step")
			self.step()

			if self.__pause.isSet() :
				self.pauseActions()

				while not self.__restart.isSet() :
					self.__restart.wait()

		self.postActions()

		self.tController.stop()

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	@abstractmethod
	def step(self) :
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
			self.__tcPA = False

	def startThymioController(self) :
		self.tController.start()

	def stopThymioController(self) :
		self.tController.stop()

	def notify(self, **params) :
		self.mainLogger.debug("Simulation - Notifying with : " + params)
		self.controller.notify(**params)


	# --- Functions for easy thymio movement ---
	def turn(self, angle) :
		try :
			self.mainLogger.debug("turn beginning !")
			self.tController.readMotorsSpeedRequest()
			self.waitForControllerResponse()

			motorsSpeed = self.tController.getMotorSpeed()

			angularSpeed = (angle * 32.0)/9.0

			if angle < 1 and angle > -1 :
				m = np.max(motorsSpeed)
				self.tController.writeMotorsSpeedRequest(motorsSpeed)
				self.waitForControllerResponse()

			if angle > 0 :
				self.tController.writeMotorsSpeedRequest([angularSpeed + motorsSpeed[0], motorsSpeed[1] - angularSpeed])
			else :
				angularSpeed = angularSpeed * -1.0
				self.tController.writeMotorsSpeedRequest([motorsSpeed[0] - angularSpeed, motorsSpeed[1] + angularSpeed])

			self.mainLogger.debug("turn wait !")
			self.waitForControllerResponse()
			self.mainLogger.debug("turn end !")
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())


	def move(self, angle, speedLeft, speedRight) :
		try :
			self.mainLogger.debug("move beginning !")
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

			self.mainLogger.debug("move wait !")
			self.waitForControllerResponse()
			self.mainLogger.debug("move end !")
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())


	def move2(self, angle, area, minSize, maxSize, speedLeft, speedRight) :
		try :
			self.mainLogger.debug("move2 beginning !")
			if area > maxSize :
				self.tController.writeMotorsSpeedRequest([0, 0])
				return

			if area < minSize :
				self.tController.writeMotorsSpeedRequest([0, 0])
				return

			self.move(angle, speedLeft, speedRight)
			self.mainLogger.debug("move2 end !")
		except :
			self.mainLogger.critical('Simulation - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())


	@staticmethod
	def checkForCompParams() :
		for param in Simulation.compParams :
			if not Params.params.checkParam(param) :
				self.mainLogger.error("Simulation - Parameter " + param + " not found.")
				return False

		return True
