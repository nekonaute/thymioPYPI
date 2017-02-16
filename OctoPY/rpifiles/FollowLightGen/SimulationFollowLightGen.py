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
import Genome
import Params

class SimulationFollowLightGen(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		
		# initialisations
		self.ls = LightSensor.LightSensor(mainLogger) 	# capteur de lumière				
		self.ls.initCam()						# initialisation de la caméra
		self.genome = Genome.Genome(mainLogger,size=18) 		# (7 capteurs de proximité, 1 biais, 1 entrée binaire pour la lumière) * 2 (moteurs)
		self.genomeList = []						# liste de couples contenant les génomes reçus et la fitness associée
		self.iter = 1							# nombre d'itérations
		self.fitness = 0							# fitness du robot
		self.lifetime = Params.lifetime
		

	def preActions(self) :
		self.log("SimulationFollowLightGen - preActions()")
		self.tController.writeColorRequest([99,0,0])
		self.waitForControllerResponse()
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()		


	def postActions(self) :
		self.log("SimulationFollowLightGen - postActions()")
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()
		self.tController.writeColorRequest([0,0,0])
		self.waitForControllerResponse()	
		
		self.ls.killCam()

	def step(self) :
		
		# evaluation de la génération
		if self.iter%self.lifetime != 0:
			if self.genome!=None:
				self.move()
				self.fitness = self.computeFitness()
				self.broadcast(self.genome,self.fitness)
			
			incomingGenomes = self.getGenomeFromOther()
			if incomingGenomes != []: # on peut se passer de ce test car on concatene
				self.genomeList+=incomingGenomes
			
		# changement de génération	
		else:
			self.log("nbite = "+str(self.iter))
			self.genome = self.genome.mutationGaussienne()
			if len(self.genomeList) > 0:
				self.genome = self.applyVariation(self.select(self.genomeList))

		self.iter+=1
		time.sleep(0.5)
		
	def getSensors(self):
		
		l = []
		
		self.tController.readSensorsRequest()
		self.waitForControllerResponse()
		proxSensors = self.tController.getPSValues()
		
		for i in range(7):
			l.append(proxSensors[i]/ Params.maxProxSensorValue)
			
		l.append(self.ls.lightCaptor())
	
		return l
		
	"""
	Fonctions de l'algorithme VanillaEE
	"""
	
	def move(self):
		sensors = self.getSensors()
		l, r = self.genome.evaluation(sensors)
		
		self.tController.writeMotorsSpeedRequest([l, r])
		self.waitForControllerResponse()
	
	def computeFitness(self):
		return 0
	
	def broadcast(self,genome,fitness):
		pass
		
	def getGenomeFromOther(self):
		return []
		
	def select(self,genomes):
		return genomes
		
	def applyVariation(self,selectedGenomes):
		return selectedGenomes		
		
		
		
		
		
		
		
		
		
		
		
		
		# raspberry8
		#put ~/thymioPYPI/OctoPY/rpifiles/FollowLightGen ~/dev/thymioPYPI/OctoPY/rpifiles