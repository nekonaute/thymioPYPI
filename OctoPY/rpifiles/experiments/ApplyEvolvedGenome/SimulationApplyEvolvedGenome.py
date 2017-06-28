#!/usr/bin/env/python
# -*- coding: utf-8 -*- 

"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Application d'un génome évolué avec SimulationFollowLightGen(Bis)(Online)
"""

import Simulation
import Params
import logging
import time

import LightSensor
import Genome

class SimulationApplyEvolvedGenome(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		
		self.mainLogger = mainLogger
		#self.mainLogger.setLevel(logging.INFO)		
		
		# initialisations
		self.ls = LightSensor.LightSensor(self.mainLogger) 	# capteur de lumière	
			
		genes = Params.params.genome.split(",") # genome que l'on veut appliquer
		for i in range(len(genes)):
			genes[i] = float(genes[i])
		
		self.genome = Genome.Genome(self.mainLogger, geneValue=genes)
		
	def preActions(self) :
		self.mainLogger.debug("SimulationApplyEvolvedGenome - preActions()")
		
		self.ls.start()		
		
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()	

	def postActions(self) :
		self.mainLogger.debug("SimulationApplyEvolvedGenome - postActions()")
		
		self.ls.shutdown()

	def step(self) :
		self.move()
		time.sleep(Params.params.wait)
		
	def getSensors(self):
		
		l = []
		
		self.tController.readSensorsRequest()
		self.waitForControllerResponse()
		proxSensors = self.tController.getPSValues()
		
		for i in range(7):
			l.append(proxSensors[i]/Params.params.maxProxSensorValue)
			
		new_res,res = self.ls.get_light_data()
		if res!=None:
			self.lightValue, lightLR = res
		else:
			self.lightValue, lightLR = (150,1)
		
		l.append(lightLR)
	
		return l
		
	def move(self):
		sensors = self.getSensors()
		l, r = self.genome.evaluation(sensors)
		
		self.left=l
		self.right=r
		
		self.tController.writeMotorsSpeedRequest([l, r])
		self.waitForControllerResponse()	
		
		
	# raspberry 3,8
	#set config_ApplyEvolvedGenome.cfg
	#put rpifiles/experiments/ApplyEvolvedGenome ~/dev/thymioPYPI/OctoPY/rpifiles/experiments/
	#put rpifiles/experiments/config_ApplyEvolvedGenome.cfg ~/dev/thymioPYPI/OctoPY/rpifiles/experiments/
	#get ~/dev/thymioPYPI/OctoPY/rpifiles/log/MainController.log /home/pi/log
