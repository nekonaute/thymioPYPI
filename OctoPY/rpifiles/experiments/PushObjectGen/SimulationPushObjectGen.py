#!/usr/bin/env/python
# -*- coding: utf-8 -*- 

"""
Stage UPMC ISIR 2017
Encadrant : Nicolas Bredeche

@author Parham SHAMS

Comportement évolutionniste de poussage d'objet basé sur VanillaEE
"""
import time
import random
import ast
import logging
import subprocess
import numpy as np

import Simulation
import Params

import LightSensor
import Genome

class SimulationPushObjectGen(Simulation.Simulation) :
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
		
		self.mainLogger.debug("SimulationPushObjectGen - __init__()")
		
		# initialisations
		self.ls = LightSensor.LightAndTagSensor(self.mainLogger) 	# capteur de lumière
		self.genome = Genome.Genome(mainLogger,size=18) 	# (7 capteurs de proximité, 1 biais, 1 entrée binaire pour la lumière) * 2 (moteurs)
		self.genomeList = []						# liste de couples contenant les génomes reçus et la fitness associée
		self.fitnessList = []						# Liste des fitnesses calculées durant une génération
		self.iter = 1								# nombre d'itérations total
		self.fitness = [0,0]						# couple fitness1 et fitness 2 du robot
		self.fitnessWindow = []						# valeurs de fitness du robot		
		self.hostname = None						# hostname
		self.tags_ids = []
		self.histo_size = 40
		
		# Braitenberg
		
		self.__probaTurn = 0.001

	def preActions(self) :
		self.mainLogger.debug("SimulationPushObjectGen - preActions()")
		
		# hostname 
		if self.hostname == None :
			proc = subprocess.Popen(["hostname"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			(out, err) = proc.communicate()
			self.hostname = out.rstrip()
			proc.wait()
		
		# Genome we want to spread
		if self.hostname=="pi3no22":
			genes = Params.params.genome.split(",") # genome que l'on veut appliquer
			for i in range(len(genes)):
				genes[i] = float(genes[i])
		
			self.genome = Genome.Genome(self.mainLogger, geneValue=genes)
		
	
		self.mainLogger.simu("======================================")
		self.mainLogger.simu("====== SimulationPushObjectGen ======")
		self.mainLogger.simu("======================================")
		self.mainLogger.simu("-------------------")
		self.mainLogger.simu("Parameters :")
		self.mainLogger.simu("duration "+str(Params.params.duration))
		self.mainLogger.simu("lifetime "+str(Params.params.lifetime))
		self.mainLogger.simu("sleep "+str(Params.params.wait))
		self.mainLogger.simu("windowSize "+str(Params.params.windowSize))
		self.mainLogger.simu("probabilities pcopy pgauss prandom "+str(Params.params.pcopy)+" "+str(Params.params.pgauss)+" "+str(1-Params.params.pcopy-Params.params.pgauss))
		self.mainLogger.simu("sigma "+str(Params.params.sigma))
		self.mainLogger.simu("-------------------")
		self.mainLogger.simu("Start :")
		
		self.ls.start()		
		
		#self.tController.writeSoundRequest([200,1])
		self.waitForControllerResponse()
		

	def postActions(self) :
		self.mainLogger.debug("SimulationPushObjectGen - postActions()")		
		
		self.mainLogger.simu("-------------------")
		self.mainLogger.simu("End :")
		self.mainLogger.simu("fitness_champion "+str(self.fitness))
		self.mainLogger.simu("champion "+str(self.genome.gene))
		self.mainLogger.simu("======================================")
		
		self.ls.shutdown()

	def step(self) :
		self.mainLogger.debug("SimulationFollowLigtGen - step()")
		"""
		# Braitenberg		
		if self.iter%Params.params.lifetime==0 and (self.iter/Params.params.lifetime)%5==0:
			#self.mainLogger.simu("SimulationPushObjectGen - step() : BRAITENBERG")
			self.tController.writeColorRequest([32, 32, 32])
			self.waitForControllerResponse()
			for z in xrange(20*Params.params.lifetime):
				try :
					self.tController.readSensorsRequest()
					self.waitForControllerResponse()
					PSValues = self.tController.getPSValues()
		
					noObstacle = True
					for i in range(5) :
						if PSValues[i] > 0 :
							noObstacle = False
							break
		
					if noObstacle :
						# Probability to do a left a right turn
						rand = random.random()
		
						if rand < self.__probaTurn :
							rand = random.random()
		
							if rand < 0.5 :
								self.tController.writeMotorsSpeedRequest([200, 0])
							else :
								self.tController.writeMotorsSpeedRequest([0, 200])
							self.waitForControllerResponse()
							time.sleep(0.5)
		
						self.tController.writeMotorsSpeedRequest([500, 500])
					else :
						self.Braitenberg(PSValues)
				except :
					self.mainLogger.critical('SimulationDefault - Unexpected error : ')# + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
				z+=1
				#time.sleep(Params.params.wait)
			self.iter+=Params.params.lifetime-1
			#self.mainLogger.simu("SimulationPushObjectGen - step() : FIN BRAITENBERG")
			self.tController.writeColorRequest([0, 0, 0])
			self.waitForControllerResponse()
				
		"""		
		# Fin Braitenberg
		if True:
			"""
			# evaluation de la génération
			if self.iter%Params.params.lifetime != 0:
				if self.genome!=None:
					self.move()
					if self.iter%Params.params.lifetime>Params.params.windowSize:
						self.fitness = self.computeFitness()
						self.broadcast(self.genome,self.fitness)
			"""
			# evaluation de la génération
			if self.iter%Params.params.lifetime != 0:
				if self.genome!=None:
					self.move()
					if self.iter%Params.params.lifetime>Params.params.windowSize:
						self.fitness = self.computeFitness()
						self.fitnessList.append(self.fitness)
						if self.iter%Params.params.lifetime==Params.params.lifetime/2-1:
							fitnessNP = np.asarray(self.fitnessList)
															
							#self.broadcast(self.genome,np.mean(fitnessNP,axis=0))
							self.broadcast(self.genome,np.max(fitnessNP,axis=0))
							#self.broadcast(self.genome,np.min(fitnessNP,axis=0))
						
						if self.iter%Params.params.lifetime==Params.params.lifetime-1:
							fitnessNP = np.asarray(self.fitnessList)
															
							#self.broadcast(self.genome,np.mean(fitnessNP,axis=0))
							self.broadcast(self.genome,np.max(fitnessNP,axis=0))
							#self.broadcast(self.genome,np.min(fitnessNP,axis=0))
							
							self.fitnessList = []
				# réception des (fitness,génome) des autres robots implicite grâce à receiveComMessage()	
			# changement de génération	
			else:
				if self.genome!=None:
					self.mainLogger.simu(str(self.iter/Params.params.lifetime)+" generation ended "+str(self.fitness))
					#self.genome = None
					self.fitnessWindow = []
				
				self.tController.writeMotorsSpeedRequest([150,150])
				self.waitForControllerResponse()
				
				if len(self.genomeList) > 0:
					#self.mainLogger.simu("SimulationPushObjectGen - step() : len(genomeList)"+str(len(self.genomeList)))
					self.genome = self.applyVariation(self.select(self.genomeList),Params.params.sigma)
				else:
					self.genome = self.applyVariation(self.genome,Params.params.sigma*1000)
					self.mainLogger.critical("SimulationPushObjectGen - step() : NE DOIT PAS ARRIVER")
	
				self.genomeList=[]	
				
		if self.iter>=Params.params.duration+Params.params.duration/5:
			self.stop()

		self.iter+=1
		time.sleep(Params.params.wait)		
		
		"""
		self.tController.readMicRequest()
		self.waitForControllerResponse()
		new = self.tController.isNewValue("MicValues")
		micIntensity = self.tController.getMicValues()
		micIntensity = int(micIntensity[0])
		if new and micIntensity!=0:
			self.mainLogger.simu("micIntensity = "+ str(micIntensity) +" "+ str(type(micIntensity))+" "+str(type(self.tController.getMicValues())))
			time.sleep(2)
		"""	
		
	def getSensors(self):
		
		l = []
		
		self.tController.readSensorsRequest()
		self.waitForControllerResponse()
		proxSensors = self.tController.getPSValues()
		
		for i in range(7):
			l.append(proxSensors[i]/Params.params.maxProxSensorValue)
			
		new_res,res = self.ls.get_data()
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
		
		self.tController.writeMotorsSpeedRequest([l, r])
		self.waitForControllerResponse()		
	
	def computeFitness(self):
		w = Params.params.windowSize
		if len(self.fitnessWindow) == w:
			self.fitnessWindow.pop(0)

		# récupération des capteurs
		max_sensors = 0.0
		proxSensors = self.getSensors()[:-1]
		for i in xrange (len(proxSensors)):
			max_sensors = max(max_sensors,proxSensors[i])
								
		speedValue = (self.getTransitiveAcceleration()) * \
				   (1 - self.getAngularAcceleration())
		
		evitement = (1 - max_sensors)
		
		if speedValue<0:
			speedValue=0					
							
		self.fitnessWindow.append([speedValue,evitement])

		#self.mainLogger.info(str((self.getTransitiveAcceleration()))+" "+str((1 - self.getAngularAcceleration()))+" "+str((1 - max_sensors))+" "+str(self.lightValue))		
		
		cur_fit1 = 0.0
		cur_fit2 = 0.0

		for f in self.fitnessWindow:
			cur_fit1 += f[0]
			cur_fit2 += f[1]
		
		return [cur_fit1/len(self.fitnessWindow),cur_fit2/len(self.fitnessWindow)]
		
	def getTransitiveAcceleration(self):
		if self.left<0 or self.right<0:
			return 0
		else:
			return abs(self.left + self.right) / (2*Params.params.maxSpeedValue)
		
	def getAngularAcceleration(self):
		return abs(self.left - self.right) / (2*Params.params.maxSpeedValue)
	
	def broadcast(self,genome,fitness):
		try :
			currRecipientsList = self.hostname
			recipientsList = Params.params.hostnames
			#recipientsList = recipientsList.split(',')
			idsList = Params.params.ids
			idsList = idsList.split(',')
			
			for i in xrange(len(idsList)):
				for j in self.tags_ids:
					if int(idsList[i]) in j:
						currRecipientsList+=","
						currRecipientsList+=str(recipientsList[i])
						break
			
			myValue = str(fitness[0])+'$'+str(fitness[1])+'$'+str(genome.gene)			
			
			#self.mainLogger.simu("broadcast - "+currRecipientsList)
			#self.sendMessage(recipients = currRecipientsList, value = myValue)    
			self.sendMessage(recipients = recipientsList, value = myValue)          
		except :
			self.mainLogger.error('"SimulationPushObjectGen - error in broadcast()' )
		
	def getGenomeFromOther(self):
		return []
		
	def select(self,genes):
		""" 
		Selectionne un genome parmis ceux contenus dans genes, en effectuant 
		une sélection en fit prop (en aggregant les deux fitnesses par une somme ponderee)
		parmi les solutions non dominées au sens de Pareto (max f1 et max f2)
		"""
		
		self.mainLogger.debug("SimulationPushObjectGen - select()")
		
		l=list(genes)
		
		# on calcule les solutions non dominees au sens de Pareto (max f1 max f2)
		f1=[]
		f2=[]
		to_remove=[] #liste des indices des dominés
		for i in range(len(l)):
			f1.append(l[i][0][0])
			f2.append(l[i][0][1])
		pareto = self.pareto_frontier(f1,f2)		

		for i in range(len(l)):
			if l[i][0][0] not in pareto[0] or l[i][0][1] not in pareto[1]:
				to_remove.append(i)
				
		to_remove.reverse()
		for i in to_remove:
			l.remove(i)
			
		if len(l)==0:
			self.mainLogger.critical("SimulationPushObjectGen - select() : pas de solution retenue")		
		
		s = 0.0
		for i in xrange(len(l)):
			s+=0.5*l[i][0][0]+0.5*l[i][0][1]
		if s!=0:
			lbis=[i[0]/s for i in l] 
			cumsum_array=np.cumsum(lbis)
			rand = random.random()
			for j in xrange(len(cumsum_array)):
				if rand<=cumsum_array[j]:
					return Genome.Genome(self.mainLogger,geneValue=l[j][1])
		else:
			self.mainLogger.simu("SimulationPushObjectGen - select() : somme des fitness ponderee est nulle")
			return Genome.Genome(self.mainLogger,geneValue=l[0][1]) 			
			
			
	def applyVariation(self,selectedGenome,sigma):
		l=[]
		l.append(Params.params.pcopy)
		l.append(Params.params.pgauss)
		l.append(1-Params.params.pcopy-Params.params.pgauss)
		rand = random.random()
		cumsum=np.cumsum(l)
		if rand<=cumsum[0]:
			return selectedGenome
		elif rand<=cumsum[1]:
			return selectedGenome.mutationGaussienne(sigma)
		elif rand<=cumsum[2]:
			if self.iter/Params.params.lifetime>30:
				return selectedGenome.mutationGaussienne(sigma)
			a,b,c=random.randint(0,255),random.randint(0,255),random.randint(0,255)
			self.tController.writeColorRequest([a, b, c])
			self.waitForControllerResponse()
			self.mainLogger.simu("SimulationFollowLightGen - applyVariation() : NEW RANDOM GENOME")
			return Genome.Genome(self.mainLogger,size=18)
		else:
			self.mainLogger.critical("SimulationFollowLightGen - applyVariation() : problem with the probabilities of mutation")
		
		return selectedGenome.mutationGaussienne(sigma)	
		
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
					fitness = [float(value[0]),float(value[1])]
					gene = ast.literal_eval(value[2])
					
					self.genomeList.append((fitness,gene))
					
					#self.mainLogger.debug("RECEIVED MESSAGE FROM: " + str(sender)+ "\n MESSAGE :" + str(value))
				else :
					self.mainLogger.error('SimulationPushObjectGen - Receiving message from ' + str(sender) + ' without value data : ' + str(data))
		else :
			self.mainLogger.error('SimulationPushObjectGen - Receiving message without sender : ' + str(data))	
	
	def Braitenberg(self, proxSensors) :
		
		leftWheel = [0.1, 0.05, 0.001, -0.06, -0.15]
		rightWheel = [-0.12, -0.07, 0.002, 0.055, 0.11]

		# Braitenberg algorithm
		totalLeft = 0
		totalRight = 0
		for i in range(5) :
			value = 0.0

			if proxSensors[i] > 0.0 :
				value = 4500 - proxSensors[i]

				if value < 0.0 :
					value = 0.0

			# self.log(str(i) + "/" + str(proxSensors[i]) + "/" + str(value))
			totalLeft = totalLeft + (value * leftWheel[i])
			totalRight = totalRight + (value * rightWheel[i])

		# Add a constant speed
		# if not avoidance :
		# 	totalRight = totalRight + 150
		# 	totalLeft = totalLeft + 150
		# else :
		totalRight = totalRight + 200
		totalLeft = totalLeft + 200

		self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])

		return True
	
	def pareto_frontier(Xs, Ys, maxX = True, maxY = True):
		"""
		Fonction qui renvoie la frontiere de Pareto des points donnes en parametre par les listes Xs et Ys.
		Par defaut maxX et maxY sont a True, ce qui signifie que l'on renvoie la frontiere de Pareto 
		correspndant a la maximisation en X et en Y
		"""
		# Sort the list in either ascending or descending order of X
		myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
		# Start the Pareto frontier with the first value in the sorted list
		p_front = [myList[0]]    
		# Loop through the sorted list
		for pair in myList[1:]:
			if maxY: 
				if pair[1] >= p_front[-1][1]: # Look for higher values of Y…
					p_front.append(pair) # … and add them to the Pareto frontier
			else:
				if pair[1] <= p_front[-1][1]: # Look for lower values of Y…
					p_front.append(pair) # … and add them to the Pareto frontier
		# Turn resulting pairs back into a list of Xs and Ys
		p_frontX = [pair[0] for pair in p_front]
		p_frontY = [pair[1] for pair in p_front]
		return p_frontX, p_frontY
		
		
		#set config_PushObjectGen.cfg
		#put rpifiles/experiments/PushObjectGen ~/dev/thymioPYPI/OctoPY/rpifiles/experiments
		#put rpifiles/experiments/config_PushObjectGen.cfg ~/dev/thymioPYPI/OctoPY/rpifiles/experiments
		#put /home/pi/thymioPYPI/OctoPY/rpifiles/ThymioController.py ~/dev/thymioPYPI/OctoPY/rpifiles/ThymioController.py
