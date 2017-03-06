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
import random
import ast
import subprocess

import Simulation
import Params

import LightSensor
import Genome


class SimulationFollowLightGen(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		
		self.mainLogger = mainLogger
		#self.mainLogger.setLevel(logging.INFO)		
		
		# initialisations
		self.ls = LightSensor.LightSensor(mainLogger) 	# capteur de lumière				
		self.ls.initCam()							# initialisation de la caméra
		self.genome = Genome.Genome(mainLogger,size=18) 	# (7 capteurs de proximité, 1 biais, 1 entrée binaire pour la lumière) * 2 (moteurs)
		self.genomeList = []						# liste de couples contenant les génomes reçus et la fitness associée
		self.iter = 1								# nombre d'itérations total
		self.fitness = 0							# fitness du robot
		self.fitnessWindow = []						# valeurs de fitness du robot		
		self.lifetime = Params.params.lifetime			# durée d'évaluation d'une génération
		self.hostname = None						# hostname
		
								

	def preActions(self) :
		if self.hostname == None :
			proc = subprocess.Popen(["hostname"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			(out, err) = proc.communicate()
			self.hostname = out.rstrip()
		
		self.mainLogger.debug("SimulationFollowLightGen - preActions()")
		
		self.tController.writeColorRequest([99,0,0])
		self.waitForControllerResponse()
		self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()				


	def postActions(self) :
		self.mainLogger.debug("SimulationFollowLightGen - postActions()")
		
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()
		self.tController.writeColorRequest([0,0,0])
		self.waitForControllerResponse()
		
		self.ls.killCam()

	def step(self) :
		self.mainLogger.debug("SimulationFollowLigtGen - step()")
		# evaluation de la génération
		if self.iter%self.lifetime != 0:
			if self.genome!=None:
				self.move()
				self.fitness = self.computeFitness()
				self.broadcast(self.genome,self.fitness)
			
			# réception des (fitness,génome) des autres robots implicite grâce à receiveComMessage()
			
		# changement de génération	
		else:
			self.mainLogger.info("SimulationFollowLightGen - step() : generation n°"+str((self.iter/self.lifetime)))
			self.mainLogger.info("SimulationFollowLightGen - step() : fitness :"+str(self.fitness))
			self.genome = None
			self.tController.writeMotorsSpeedRequest([0, 0])
			self.waitForControllerResponse()
			
			
			if len(self.genomeList) > 0:
				self.genome = self.applyVariation(self.select(self.genomeList))

			self.genomeList=[]			
			
		self.iter+=1
		time.sleep(0.5)
		
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
		
	"""
	Fonctions de l'algorithme VanillaEE
	"""
	
	def move(self):
		sensors = self.getSensors()
		l, r = self.genome.evaluation(sensors)
		
		self.left=l
		self.right=r
		
		self.mainLogger.info(str(l)+" "+str(r))
		
		self.tController.writeMotorsSpeedRequest([l, r])
		self.waitForControllerResponse()		
	
	def computeFitness(self):
		w = Params.params.windowSize
		if len(self.fitnessWindow) == w:
			self.fitnessWindow.pop(0)

		# récupération des cap
		mean_sensors = 0.0
		proxSensors = self.getSensors()[:-1]
		for i in xrange (len(proxSensors)):
			mean_sensors += proxSensors[i]
		mean_sensors/=len(proxSensors)
								
		speedValue = (self.getTransitiveAcceleration()) * \
				   (1 - self.getAngularAcceleration()) * \
				   (1 - mean_sensors)
							
		self.fitnessWindow.append(self.lightValue * speedValue)

		self.mainLogger.info(str((self.getTransitiveAcceleration()))+" "+str((1 - self.getAngularAcceleration()))+" "+str((1 - mean_sensors))+" "+str(self.lightValue))		
		
		cur_fit = 0.0
		for f in self.fitnessWindow:
			cur_fit += f	
		
		return cur_fit/len(self.fitnessWindow)
		
	def getTransitiveAcceleration(self):
		return abs(self.left + self.right) / (2*Params.params.maxSpeedValue)
		
	def getAngularAcceleration(self):
		return abs(self.left - self.right) / (2*Params.params.maxSpeedValue)
	
	def broadcast(self,genome,fitness):
		if(random.random()<1.0):		
			try :
				recipientsList = Params.params.hostnames
				myValue = str(fitness)+'$'+str(genome.gene)			
					
				self.sendMessage(recipients = recipientsList, value = myValue)              
			except :
				self.mainLogger.critical('"SimulationFollowLightGen - broadcast()' )
		
	def getGenomeFromOther(self):
		return []
		
	def select(self,genes):
		# TODO comportement par défaut best
		best_i = 0
		best_fit = 0
		
		for i in range(len(genes)):
			if genes[i][0] > best_fit:
				best_fit=genes[i][0]
				best_i=i
				
		selectedGene = genes[best_i][1]
		
		return Genome.Genome(self.mainLogger,geneValue=selectedGene)
		
	def applyVariation(self,selectedGenome):
		return selectedGenome.mutationGaussienne()	
		
	"""
	Fonctions de communications
	"""	
		
	def receiveComMessage(self, data) :
		"""
		'overridée' pour recevoir les messages des autres robots.
		"""
		
		sender = ""
		value = []
		if "senderHostname" in data.keys() :
			sender = data["senderHostname"]
			if sender!=self.hostname:
				if "value" in data.keys():
					value = data["value"].split("$")
					fitness = float(value[0])
					gene = ast.literal_eval(value[1])
					
					self.genomeList.append((fitness,gene))
					
					#self.mainLogger.debug("RECEIVED MESSAGE FROM: " + str(sender)+ "\n MESSAGE :" + str(value))
				else :
					self.mainLogger.error('SimulationFollowLightGen - Receiving message from ' + str(sender) + ' without value data : ' + str(data))
		else :
			self.mainLogger.error('SimulationFollowLightGen - Receiving message without sender : ' + str(data))	
		
		

		# raspberry 3,8
		#set config_FollowLightGen.cfg
		#put ~/thymioPYPI/OctoPY/rpifiles/FollowLightGen ~/dev/thymioPYPI/OctoPY/rpifiles
		#put ~/thymioPYPI/OctoPY/rpifiles/config_FollowLightGen.cfg ~/dev/thymioPYPI/OctoPY/rpifiles
		#get ~/dev/thymioPYPI/OctoPY/rpifiles/log/MainController.log /home/pi/log