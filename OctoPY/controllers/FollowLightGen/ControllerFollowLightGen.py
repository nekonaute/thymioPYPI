#!/usr/bin/env/python
# -*- coding: utf-8 -*-

"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Controleur principal du comportement évolutionniste de suivi de lumière.
"""

import time

from controllers import Controller
from controllers import Params

from utils import MessageType

class ControllerFollowLightGen(Controller.Controller) :
	def __init__(self, controller, mainLogger) :
		Controller.Controller.__init__(self, controller, mainLogger)
		
		self.stepp=0
		self.max=5 # en secondes
		
	def preActions(self) :	
		
		if self.octoPYInstance.hashThymiosHostnames :
			# Init all robots
			self.log("Send init...")
			self.octoPYInstance.sendMessage(MessageType.INIT, [])
			time.sleep(2)

			# Load simulation
			self.log("Load simulation...")
			self.octoPYInstance.sendMessage(MessageType.SET, [], "config_FollowLightGenOnline.cfg")
			time.sleep(2)

			# Start simulation
			self.log("Start simulation...")
			self.octoPYInstance.sendMessage(MessageType.START, [])

	def postActions(self) :
		self.log("Stop simulation...")
		self.octoPYInstance.sendMessage(MessageType.STOP, [])
		time.sleep(2)

		# Kill controllers
		self.log("Kill main controller...")
		self.octoPYInstance.sendMessage(MessageType.KILL, [])
		

	def step(self) :
		self.stepp+=1
		time.sleep(1)
		self.log("seconds = "+str(self.stepp))
		if self.stepp>self.max:
			self.stop()

	def notify(self, **arg) :
		pass
