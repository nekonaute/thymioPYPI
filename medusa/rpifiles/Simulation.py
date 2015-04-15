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

		# Main controller
		self.__controller = controller

		self.__stop = threading.Event()

		# Thymio controller
		self.__tcPA = False
		self.__tcPerformedAction = threading.Condition()
		self.__tController = ThymioController.ThymioController(self, mainLogger) 
		self.__tController.start()

		self.__mainLogger = mainLogger

	def run(self) :
		self.__mainLogger.debug('hep la !')
		self.preActions()
		self.__mainLogger.debug('beuh ?')

		while not self.__stop.isSet() :
			self.step()

		self.postActions()

		self.__tController.stop()

	def preActions(self) :
		self.__mainLogger.debug('pas en arriere')
		pass

	def postActions(self) :
		pass

	@abstractmethod
	def step(self) :
		pass

	def stop(self) :
		self.__stop.set()

	def reset(self) :
		pass
		
	def thymioControllerPerformedAction(self) :
		with self.__tcPerformedAction:
			self.__tcPA = True
			self.__tcPerformedAction.notify()

	def __waitForControllerResponse(self) :
		# Wait for ThymioController response
		with self.__tcPerformedAction :
			while not self.__tcPA and not self.__stop.isSet() :
				self.__tcPerformedAction.wait()
			self.__tcPA = False

	def startThymioController(self) :
		self.__tController.start()

	def stopThymioController(self) :
		self.__tController.stop()

	@staticmethod
	def checkForCompParams() :
		for param in Simulation.compParams :
			if not Params.params.checkParam(param) :
				self.__mainLogger.error("Simulation - Parameter " + param + " not found.")
				return False

		return True
