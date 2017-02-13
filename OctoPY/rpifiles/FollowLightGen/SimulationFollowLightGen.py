#!/usr/bin/env/python
# -*- coding: utf-8 -*- 

"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Comportement évolutionniste de suivi de lumière.
"""
import time

import Simulation

import LightSensor

class SimulationFollowLightGen(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		self.ls = LightSensor.LightSensor(mainLogger)
		

	def preActions(self) :
		self.log("SimulationFollowLightGen - preActions()")
		self.tController.writeColorRequest([99,0,0])
		self.waitForControllerResponse()
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()		
		
		self.ls.initCam()

	def postActions(self) :
		self.log("SimulationFollowLightGen - postActions()")
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()
		self.tController.writeColorRequest([0,0,0])
		self.waitForControllerResponse()	
		
		self.ls.killCam()

	def step(self) :
		
		self.ls.lightCaptor()
		time.sleep(1)

		# raspberry8
		#put ~/thymioPYPI/OctoPY/rpifiles/FollowLightGen ~/dev/thymioPYPI/OctoPY/rpifiles