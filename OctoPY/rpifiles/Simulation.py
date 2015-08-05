import threading

from abc import ABCMeta, abstractmethod

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
		self.preActions()

		while not self.__stop.isSet() :
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

	@staticmethod
	def checkForCompParams() :
		for param in Simulation.compParams :
			if not Params.params.checkParam(param) :
				self.mainLogger.error("Simulation - Parameter " + param + " not found.")
				return False

		return True
