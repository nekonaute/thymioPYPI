#!/usr/bin/env/python
# -*- coding: utf-8 -*- 

"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Comportement évolutionniste de suivi de lumière basé sur (1+1) Online
"""
import time
import logging
import random

import Simulation
import Params

import LightSensor
import Genome
#from tag_recognition import Tag_Detector


class SimulationFollowLightGenOnline(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		
		self.mainLogger = mainLogger
		self.mainLogger.setLevel(logging.CRITICAL)		
		
		# initialisations
		self.ls = LightSensor.toto(self.mainLogger) 	# capteur de lumière				
		#self.ls.initCam()							# initialisation de la caméra
		self.champion = Genome.Genome(mainLogger,size=18) # (7 capteurs de proximité, 1 biais, 1 entrée binaire pour la lumière) * 2 (moteurs)
		self.challenger = None		
		self.generation = 1							# nombre de generation total
		self.fitnessChampion = 0						# fitness du champion
		self.fitnessChallenger = 0					# fitness du challenger
		self.sigma = Params.params.sigma				# sigma
		self.sleep = 0.001

	def preActions(self) :
		self.mainLogger.debug("SimulationFollowLightGenOnline - preActions()")
	
		self.mainLogger.info("SimulationFollowLightGen - preActions() : PARAMETRES\n"+str(Params.params.lifetime))		
		self.ls.start()		
		
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()	

	def postActions(self) :
		self.mainLogger.debug("SimulationFollowLightGenOnline - postActions()")
		self.mainLogger.info("SimulationFollowLightGenOnline - postActions() :"+str(self.fitnessChampion))
		self.mainLogger.info("SimulationFollowLightGenOnline - postActions() :"+str(self.champion.gene))
		
		self.ls.shutdown()

	def step(self) :
		self.mainLogger.critical("SimulationFollowLigtGenOnline - step()")
		new_res,res = self.ls.get_light_data()
		self.mainLogger.critical(str(res))
		self.mainLogger.critical(str(new_res))
	
		# N génération passée		
		if(self.generation == Params.params.N):
			self.stop()
		
		if random.random() < Params.params.Preevaluate or self.generation==1:
			self.mainLogger.info("SimulationFollowLigtGenOnline - step() : reevaluate champion")	
			self.recover(self.champion)
			self.runAndEvaluate(self.champion,"champion")
		else :	
			self.challenger = self.applyVariation(self.champion, self.sigma)
			self.runAndEvaluate(self.challenger,"challenger")
			
			self.mainLogger.critical("SimulationFollowLigtGenOnline - step() : old fitness : "+str(self.fitnessChampion))
			self.mainLogger.critical("SimulationFollowLigtGenOnline - step() : new fitness : "+str(self.fitnessChallenger))
				
			if self.fitnessChallenger > self.fitnessChampion:
				self.mainLogger.info("SimulationFollowLigtGenOnline - step() : nouveau champion")				
				self.champion = self.challenger
				self.fitnessChampion = self.fitnessChallenger
				self.sigma = Params.params.minSigma
			else :
				self.sigma = min(Params.params.maxSigma, self.sigma*2)
			
		self.generation+=1
		time.sleep(self.sleep)
		
	"""
	Fonctions de l'algorithme (1+1)-Online
	"""
	
	def runAndEvaluate(self, candidate, nameCandidate):
		self.fitnessChallenger=0
		
		for i in range(Params.params.lifetime):
			self.move(candidate)
			self.computeFitness(nameCandidate)
				
			time.sleep(self.sleep)	
	
	def recover(self, candidate):
		for i in range(Params.params.lifetime):
			
			self.move(candidate)
			
			time.sleep(self.sleep)
			
	def getSensors(self):
		
		l = []
		
		self.tController.readSensorsRequest()
		self.waitForControllerResponse()
		proxSensors = self.tController.getPSValues()
		
		for i in range(7):
			l.append(proxSensors[i]/Params.params.maxProxSensorValue)
			
		new_res,res = self.ls.get_light_data()
		self.mainLogger.critical(str(res))
		self.mainLogger.critical(str(new_res))
		if res!=None:
			self.lightValue, lightLR = (150,1)
			tags =  res
			tags_contours,tags_ids,tags_distances,tags_rotations, tags_bounding_boxes = tags
			self.mainLogger.critical("tag : "+str(tags_ids))

		else:
			self.lightValue, lightLR = (150,1)
		
		self.mainLogger.critical("More left :"+str(lightLR))
		l.append(lightLR)
	
		return l
	
	def move(self, candidate):
		sensors = self.getSensors()
		l, r = candidate.evaluation(sensors)
		
		self.left=l
		self.right=r
		
		self.tController.writeMotorsSpeedRequest([l, r])
		self.waitForControllerResponse()			
	
	def computeFitness(self, nameCandidate):
		# récupération des capteurs
		max_sensors = 0.0
		proxSensors = self.getSensors()[:-1]
		for i in xrange (len(proxSensors)):
			max_sensors = max(max_sensors,proxSensors[i])
								
		speedValue = (self.getTransitiveAcceleration()) * \
				   (1 - self.getAngularAcceleration()) * \
				   (1 - max_sensors)#*self.lightValue
						
		self.mainLogger.info(str((self.getTransitiveAcceleration()))+" "+str((1 - self.getAngularAcceleration()))+" "+str((1 - max_sensors))+" "+str(self.lightValue))		
		
		if(nameCandidate=="champion"):
			self.fitnessChampion = self.fitnessChampion + speedValue
		elif(nameCandidate=="challenger"):	
			self.fitnessChallenger = self.fitnessChallenger + speedValue
		
	def getTransitiveAcceleration(self):
		return abs(self.left + self.right) / (2*Params.params.maxSpeedValue)
		
	def getAngularAcceleration(self):
		return abs(self.left - self.right) / (2*Params.params.maxSpeedValue)
		
	def applyVariation(self,selectedGenome, sigma):
		return selectedGenome.mutationGaussienne(sigma)
		
		
	# raspberry 3,8
	#set config_FollowLightGenOnline.cfg
	#put ~/thymioPYPI/OctoPY/rpifiles/FollowLightGenOnline ~/dev/thymioPYPI/OctoPY/rpifiles
	#put ~/thymioPYPI/OctoPY/rpifiles/config_FollowLightGenOnline.cfg ~/dev/thymioPYPI/OctoPY/rpifiles
	#get ~/dev/thymioPYPI/OctoPY/rpifiles/log/MainController.log /home/pi/log