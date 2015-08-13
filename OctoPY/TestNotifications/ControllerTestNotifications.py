#!/usr/bin/env/python

import time

import Controller
import OctoPY
import Params

from utils import MessageType

MAX = 100

class ControllerTestNotifications(Controller.Controller) :
	def __init__(self, controller, mainLogger) :
		Controller.Controller.__init__(self, controller, mainLogger)

		self.__total = 0

	def preActions(self) :
		if OctoPY.hashThymiosHostnames :
			# Init all robots
			OctoPY.sendMessage(MessageType.INIT, [])
			time.sleep(5)

			# Register on all robots
			OctoPY.register([])

			# Load simulation
			OctoPY.sendMessage(MessageType.SET, [], "config_TestNotifications.cfg")

			# Start simulation
			OctoPY.sendMessage(MessageType.START, [])

	def postActions(self) :
		# Stop simulation
		OctoPY.sendMessage(MessageType.STOP, [])

		# Kill controllers
		OctoPY.sendMessage(MessageType.KILL, [])

	def step(self) :
		pass

	def notify(self, **params) :
		self.log("Received notification from " + params["hostIP"])

		if "value" in params :
			self.log("Received value : " + str(params["value"]))
			self.__total += int(params["value"])
			self.log("Total is : " + self.__total)
		
			if self.__total >= MAX :
				self.stop()
