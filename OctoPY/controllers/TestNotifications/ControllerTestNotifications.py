#!/usr/bin/env/python

import time


from controllers import Controller
from controllers import Params

from utils import MessageType

MAX = 30

class ControllerTestNotifications(Controller.Controller) :
	def __init__(self, octoPYInstance, controller) :
		Controller.Controller.__init__(self, octoPYInstance, controller)

		self.__total = 0

	def preActions(self) :
		if self.octoPYInstance.hashThymiosHostnames :
			# Init all robots
			self.log("Send init...")
			self.octoPYInstance.sendMessage(MessageType.INIT, [])
			time.sleep(4)

			# Register on all robots
			self.log("Register...")
			self.register([])
			# time.sleep(2)

			# Load simulation
			self.log("Load simulation...")
			self.octoPYInstance.sendMessage(MessageType.SET, [], "config_TestNotifications.cfg")
			# time.sleep(2)

			# Start simulation
			self.log("Start simulation...")
			self.octoPYInstance.sendMessage(MessageType.START, [])
			#time.sleep(2)

	def postActions(self) :
		# Stop simulation
		self.log("Stop simulation...")
		self.octoPYInstance.sendMessage(MessageType.STOP, [])
		# time.sleep(2)

		# Kill controllers
		self.log("Kill controller...")
		self.octoPYInstance.sendMessage(MessageType.KILL, [])

	def step(self) :
		time.sleep(0.1)

	def notify(self, **params) :
		self.log("Received notification from " + str(params["hostIP"]))

		if "value" in params :
			self.log("Received value : " + str(params["value"]))
			self.__total += int(params["value"])
			self.log("Total is : " + str(self.__total))
		
			if self.__total >= MAX :
				self.stop()