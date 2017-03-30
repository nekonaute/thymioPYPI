#!/usr/bin/env/python

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
		self.mainLogger.setLevel(logging.INFO)		
		
		# initialisations
		self.ls = LightSensor.LightSensor(mainLogger) 					# capteur de lumière				
		self.ls.initCam()											# initialisation de la caméra
		self.genome = Genome.Genome(geneValue=Params.params.genome)		# genome que l'on veut appliquer
	def preActions(self) :
		self.mainLogger.debug("SimulationApplyEvolvedGenome - preActions()")
		
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()	

	def postActions(self) :
		self.mainLogger.debug("SimulationApplyEvolvedGenome - postActions()")
		
		self.ls.killCam()

	def step(self) :
		self.move()
		time.sleep(0.3)
		
	def getSensors(self):
		
		l = []
		
		self.tController.readSensorsRequest()
		self.waitForControllerResponse()
		proxSensors = self.tController.getPSValues()
		
		for i in range(7):
			l.append(proxSensors[i]/Params.params.maxProxSensorValue)
			
		self.lightValue, lightLR = self.ls.lightCaptor()
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
	#put ~/thymioPYPI/OctoPY/rpifiles/ApplyEvolvedGenome ~/dev/thymioPYPI/OctoPY/rpifiles
	#put ~/thymioPYPI/OctoPY/rpifiles/config_ApplyEvolvedGenome.cfg ~/dev/thymioPYPI/OctoPY/rpifiles
	#get ~/dev/thymioPYPI/OctoPY/rpifiles/log/MainController.log /home/pi/log