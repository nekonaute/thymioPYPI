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

class SimulationFollowLightGenOnline(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		
		# définition de notre niveau de log
		self.mainLogger = mainLogger		
		
		self.SIMU = logging.INFO + 1 
		logging.addLevelName(self.SIMU, "SIMU")
		
		def simu(message, *args, **kws):
		    if self.mainLogger.isEnabledFor(self.SIMU):
		        self.mainLogger._log(self.SIMU, message, args, **kws) 
		self.mainLogger.simu = simu
		
		self.mainLogger.setLevel(self.SIMU)		
		
		self.mainLogger.debug("SimulationFollowLightGenOnline - __init__()")
		
		# initialisations
		self.ls = LightSensor.LightSensor(self.mainLogger) 	# capteur de lumière	
		self.champion = Genome.Genome(mainLogger,size=18) # (7 capteurs de proximité, 1 biais, 1 entrée binaire pour la lumière) * 2 (moteurs)
		self.challenger = None		
		self.generation = 1							# nombre de generation total
		self.nbReevalued = 0
		self.fitnessChampion = 0						# fitness du champion
		self.fitnessChallenger = 0					# fitness du challenger
		self.sigma = Params.params.sigma				# sigma
		self.sleep = Params.params.wait

	def preActions(self) :
		self.mainLogger.debug("SimulationFollowLightGenOnline - preActions()")
	
		self.mainLogger.simu("======================================")
		self.mainLogger.simu("=== SimulationFollowLightGenOnline ===")
		self.mainLogger.simu("======================================")
		self.mainLogger.simu("-------------------")
		self.mainLogger.simu("Parameters :")
		self.mainLogger.simu("N "+str(Params.params.N))
		self.mainLogger.simu("lifetime "+str(Params.params.lifetime))
		self.mainLogger.simu("sleep "+str(Params.params.wait))
		self.mainLogger.simu("Preevaluate "+str(Params.params.Preevaluate))
		self.mainLogger.simu("sigma "+str(Params.params.sigma))
		self.mainLogger.simu("minSigma "+str(Params.params.minSigma))
		self.mainLogger.simu("maxSigma "+str(Params.params.maxSigma))
		self.mainLogger.simu("-------------------")
		self.mainLogger.simu("Start :")		
		
		self.ls.start()		
		
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()	

	def postActions(self) :
		self.mainLogger.debug("SimulationFollowLightGenOnline - postActions()")
		
		self.mainLogger.simu("-------------------")
		self.mainLogger.simu("End :")
		self.mainLogger.simu("fitness_champion "+str(self.fitnessChampion))
		self.mainLogger.simu("champion "+str(self.champion.gene))
		self.mainLogger.simu("======================================")		
		
		self.ls.shutdown()

	def step(self) :
		self.mainLogger.debug("SimulationFollowLigtGenOnline - step()")
	
		# N génération passée		
		if(self.generation == Params.params.N):
			self.stop()
		
		if random.random() < Params.params.Preevaluate or self.generation==1:
			self.recover(self.champion)
			self.mainLogger.simu(str(self.generation)+" champion_recovered")
			self.runAndEvaluate(self.champion,"champion")
			
			self.mainLogger.simu(str(self.generation)+" champion_reevaluated-"+str(self.nbReevalued)+" "+str(self.fitnessChampion))	
		else :	
			self.challenger = self.applyVariation(self.champion, self.sigma)
			self.runAndEvaluate(self.challenger,"challenger")
			
			self.mainLogger.simu(str(self.generation)+" challenger_evaluated "+str(self.fitnessChallenger))	
				
			if self.fitnessChallenger > self.fitnessChampion:
				self.mainLogger.simu(str(self.generation)+" new_champion "+str(self.fitnessChampion)+" "+str(self.fitnessChallenger))				
				self.champion = self.challenger
				self.fitnessChampion = self.fitnessChallenger
				self.sigma = Params.params.minSigma
				
				self.nbReevalued = 0
			else :
				self.sigma = min(Params.params.maxSigma, self.sigma*2)
			
		self.generation+=1
		time.sleep(self.sleep)
		
	"""
	Fonctions de l'algorithme (1+1)-Online
	"""
	
	def runAndEvaluate(self, candidate, nameCandidate):
		self.mainLogger.debug("SimulationFollowLigtGenOnline - runAndEvaluate()")
		
		if(nameCandidate=="champion"):
			self.fitnessChampion = 0
		elif(nameCandidate=="challenger"):	
			self.fitnessChallenger = 0
		
		for i in range(Params.params.lifetime):
			self.move(candidate)
			self.computeFitness(nameCandidate)
				
			time.sleep(self.sleep)
	
	def recover(self, candidate):
		self.mainLogger.debug("SimulationFollowLigtGenOnline - recover()") 
		
		self.nbReevalued+=1		
		
		for i in range(Params.params.lifetime):
			self.move(candidate)
			time.sleep(self.sleep)
			
		
	def computeFitness(self, nameCandidate):
		# récupération des capteurs
		max_sensors = 0.0
		proxSensors = self.getSensors()[:-1]
		for i in xrange (len(proxSensors)):
			max_sensors = max(max_sensors,proxSensors[i])
								
		speedValue = (self.getTransitiveAcceleration()) * \
				   (1 - self.getAngularAcceleration()) * \
				   (1 - max_sensors)#*self.lightValue
							
		if speedValue<0:
			speedValue=0
						
		#self.mainLogger.info(str((self.getTransitiveAcceleration()))+" "+str((1 - self.getAngularAcceleration()))+" "+str((1 - max_sensors))+" "+str(self.lightValue))		
		
		if(nameCandidate=="champion"):
			self.fitnessChampion = self.fitnessChampion + speedValue
		elif(nameCandidate=="challenger"):	
			self.fitnessChallenger = self.fitnessChallenger + speedValue
			
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
	
	def move(self, candidate):
		sensors = self.getSensors()
		l, r = candidate.evaluation(sensors)
		
		self.left=l
		self.right=r
		
		self.tController.writeMotorsSpeedRequest([l, r])
		self.waitForControllerResponse()			
		
	def getTransitiveAcceleration(self):
		return abs(self.left + self.right) / (2*Params.params.maxSpeedValue)
		
	def getAngularAcceleration(self):
		return abs(self.left - self.right) / (2*Params.params.maxSpeedValue)
		
	def applyVariation(self,selectedGenome, sigma):
		return selectedGenome.mutationGaussienne(sigma)
		
		
	# raspberry 3,8
	#set config_FollowLightGenOnline.cfg
	#put rpifiles/experiments/FollowLightGenOnline ~/dev/thymioPYPI/OctoPY/rpifiles/experiments
	#put rpifiles/experiments/config_FollowLightGenOnline.cfg ~/dev/thymioPYPI/OctoPY/rpifiles/experiments
	#get ~/dev/thymioPYPI/OctoPY/rpifiles/log/MainController.log /home/pi/log