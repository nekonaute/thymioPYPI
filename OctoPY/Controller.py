import logging
import threading

import Params

"""
OCTOPY : Controller.py

Basic model for all controllers : every controller will automatically inherit
from this class when created with CreateController.py
"""

from abc import ABCMeta, abstractmethod

class Controller(threading.Thread) :
	__metaclass__ = ABCMeta
	staticID = 0

	# Compulsory parameters
	compParams = ['controller_name', 'controller_path']

	def __init__(self, octoPYInstance, detached) :
		threading.Thread.__init__(self)

		self.octoPYInstance = octoPYInstance

		if detached :
			self.daemon = True

		self.__stop = threading.Event()
		self.__ID = Controller.getNewID()

	@staticmethod
	def getNewID() :
		Controller.staticID += 1
		return Controller.staticID - 1

	def getID(self) :
		return self.__ID

	ID = property(getID)

		
	def run(self) :
		self.preActions()

		while not self.__stop.isSet() :
			self.step()

		self.postActions()

	@abstractmethod
	def step(self) :
		pass

	def preActions(self) :
		pass

	def postActions(self) :
		pass		

	def stop(self) :
		self.__stop.set()

	def log(self, message, level = logging.DEBUG) :
		self.octoPYInstance.logger.log(level, message)

	def register(self, IPs = []) :
		self.octoPYInstance.registerController(self, IPs)

	def notify(self, **params) :
		pass

	@staticmethod
	def checkForCompParams() :
		for param in Controller.compParams :
			if not Params.params.checkParam(param) :
				print("Controller - Parameter " + param + " not found.", )
				return False

		return True