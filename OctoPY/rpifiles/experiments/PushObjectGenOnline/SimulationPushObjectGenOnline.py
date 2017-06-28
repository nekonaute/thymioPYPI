#!/usr/bin/env/python
# -*- coding: utf-8 -*- 

"""
STAGE UPMC ISIR 2017
Encadrant : Nicolas Bredeche

@author Parham SHAMS

Comportement évolutionniste de poussage d'objet basé sur (1+1) Online
"""

import time
import logging
import random

import Simulation
import Params

import LightSensor
import Genome

from tools.camera_tools.tag_recognition import CNT,IDS,DST
import numpy as np
import cv2

class SimulationPushObjectGenOnline(Simulation.Simulation) :
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
		
		self.mainLogger.debug("SimulationPushObjectGenOnline - __init__()")
		
		# initialisations
		self.ls = LightSensor.LightAndTagSensor(self.mainLogger) 	# capteur de lumière	
		self.champion = Genome.Genome(mainLogger,size=18) # (7 capteurs de proximité, 1 biais, 1 entrée binaire pour la direction de l'objet a pousser) * 2 (moteurs)
		self.challenger = None		
		self.generation = 1							# nombre de generation total
		self.nbReevalued = 0
		self.fitnessChampion = 0						# fitness du champion
		self.fitnessChallenger = 0					# fitness du challenger
		self.sigma = Params.params.sigma				# sigma
		self.sleep = Params.params.wait
		self.distList = []

	def preActions(self) :
		self.mainLogger.debug("SimulationPushObjectGenOnline - preActions()")
	
		self.mainLogger.simu("======================================")
		self.mainLogger.simu("=== SimulationPushObjectGenOnline ===")
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
		
		#self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()	

	def postActions(self) :
		self.mainLogger.debug("SimulationPushObjectGenOnline - postActions()")
		
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
		
		s=0			
		for d in self.distList:
			s+=d							
							
		speedValue = s #* \
				   #(1 - max_sensors)#*self.lightValue
				   #(1 - self.getAngularAcceleration()) * \
							
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
		
		
		newresults,tags_info = self.ls.get_data()
		"""
		if res!=None:
			self.lightValue, lightLR = res
		else:
			self.lightValue, lightLR = (150,1)
			
		if res!=None:
			self.lightValue = res[0]
			lightLR = res[1]
			
			tags_info = res[2]
			tags_contours, tags_ids, tags_distances, tags_rotations = tags_info
			self.tags_ids.append(tags_ids)
			if len(self.tags_ids)>self.histo_size:
				self.tags_ids.pop(0)
			#self.mainLogger.simu(str(self.tags_ids))
		else:
			self.lightValue, lightLR = (150,1)
			self.tags_ids.append([])
			if len(self.tags_ids)>self.histo_size:
				self.tags_ids.pop(0)	
		"""
		lightLR=0.5
		v=False
		if newresults and tags_info != None:
			v=True
			tags_info = tags_info[2]
			tag_cnt, tags_ids, tag_dist, tags_rotations = tags_info
			#tag_cnt =  tags_info[CNT]
			#tags_ids = tags_info[IDS]
			#tag_dist = tags_info[DST]
			if tag_dist != []:
				nearest = np.argmin(np.array(tag_dist))
				cnt = tag_cnt[nearest]
				M = cv2.moments(cnt)
				cx = int(M['m10']/M['m00'])
				if cx < self.image_shape[0]/2:
					lightLR=0
				else:
					lightLR=1
				self.mainLogger.simu('SimulationPushObjectGenOnline - following tag: %d' % tags_ids[nearest] +str(type(tag_dist)))
				
			else:
				tag_dist=9999999999999999999
		else:
			tag_dist=9999999999999999999
					
		self.mainLogger.simu('SimulationPushObjectGenOnline - following tag: ' +str(type(tag_dist)))
		
		if not v:
			tag_dist=0
		else:
			tag_dist=1/tag_dist
			
		self.distList.append(tag_dist)
		if len(self.distList)>=20:
			self.distList.pop(0)
		
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
	#set config_PushObjectGenOnline.cfg
	#put rpifiles/experiments/PushObjectGenOnline ~/dev/thymioPYPI/OctoPY/rpifiles/experiments
	#put rpifiles/experiments/config_PushObjectGenOnline.cfg ~/dev/thymioPYPI/OctoPY/rpifiles/experiments
	#get ~/dev/thymioPYPI/OctoPY/rpifiles/log/MainController.log /home/pi/log