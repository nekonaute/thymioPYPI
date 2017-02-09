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
import Params

import LightSensor as ls

class SimulationFollowLightGen(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		self.light = ls.initCam()
		

	def preActions(self) :
		self.log("---- PREACTIONS")
		self.tController.writeColorRequest([99,0,0])
		self.waitForControllerResponse()
		self.tController.writeSoundRequest([350,1])
		self.waitForControllerResponse()		


	def postActions(self) :
		self.log("---- POSTACTIONS")
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()
		self.tController.writeColorRequest([0,0,0])
		self.waitForControllerResponse()	

	def step(self) :
		
		print ls.lightCaptor(self.light)
		
		time.sleep(1)

		
		#put ~/thymioPYPI/OctoPY/rpifiles/FollowLightGen ~/dev/thymioPYPI/OctoPY/rpifiles