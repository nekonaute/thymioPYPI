#!/usr/bin/env/python

import Simulation
import Params

import dbus
import dbus.mainloop.glib
import gobject
import time
from ThymioFunctions import *
from optparse import OptionParser

import genome
import vision
import random
import threading
import traceback

import time


start = time.time()
runTime = 10
RESOURCES = 100
loop= gobject.MainLoop()


class SimulationVanillaEE(Simulation.Simulation) :
	
	
	def __init__(self, controller, mainLogger) :
		
		#Simulation.Simulation.__init__(self, controller, mainLogger)
		self.myGenome = genome.genome(7*2*3+2)# 7 sensor * 2 output * 3 type of thing to detect + 1 "control" value per output
		self.eye = vision.vision() #class with the technik of captation of the environnement
		self.resources = RESOURCES; # find a way to initiate all of that
		self.fitness =0;
		self.fitnessWindow = []
		self.fitnessWindowSize = 10
		self.genomePool= [] #stock the genome of the other robots
		self.fitnessPool= [] #stock the fitness of the other robots
		self.alive = True
		self.numberOfTheTournament = 5;
		self.ticks = 0
		self.generations = 400
		
		
		"""communication"""
		listRpis = Params.params.list_rpis
		self.__listRpis = listRpis.split(',')
		self.__frequencyMess = int(Params.params.frequency_mess)
		self.__maxMess = int(Params.params.max_mess)
		self.__listMessages = list()
		
		""" acceleration"""
		self.oldtransitifAcelleration= 0
		self.oldAngularAcelleration= 0

	def preActions(self) :
		pass

	def postActions(self) :
		setMotorSpeed(0, 0)

	def step(self) :
		if time.time()-start < runTime:
			self.ticks +=1
			
			#if (self.alive):
			if( self.alive):
					
				self.evaluation()
			
				self.updateFitness()
			
				print self.fitness
		
# 			self.resourcesManagement()
		
# 			self.tchatBetweenRobot()
		
			self.evolution()
			
			return True		
		if time.time()-start>=runTime:
			setMotorSpeed(0, 0)
			print 'ending loop'
			loop.quit()
			return False


	def evaluation(self):
		entry = self.eye.updateVision()
		s = ""
		for i in range (len(entry)):
			s+= str(entry[i]) + "|"
# 		print s####################################################################################
		left = self.myGenome.evaluationLeft(entry) 
		right = self.myGenome.evaluationRight(entry) 
		print "left=" +str(left) + "  right = " + str(right)
		setMotorSpeed(left, right)
		#setMotorSpeed(0, 0)
		#setMotorSpeed(100, 100)
	
	def resourcesManagement(self):
		if (self.resources > 0):
			self.resources += -1 ;
		if (self.resources == 0):
			self.alive = False
	
	def tchatBetweenRobot(self):
		self.broadcast()
		
	
	def evolution(self):
		if (self.ticks == self.generations):
			ticks = 0
			if (len(self.fitnessWindow) < self.fitnessWindowSize):
				self.fitnessWindow.append(self.fitness)
				self.fitness = 0
			
			
			else :
				child = self.tournament(self.numberOfTheTournament)
				if ( child.eqals(self.myGenome)):
					self.resources =0
					self.fitness = 0
					self.resourcesManagement()
					self.alive = 0
					
					 
				else
					self.myGenome = child.MutationGaussian(self.sigma)
					self.resources = RESOURCES
					self.alive = 1
				self.genomePool = []
				self.fitnessPool = []
				self.fitness = 0
		
		
	
	def tournament(self,tourmanentSize):
		if tourmanentSize <= 0 :
			print "ERROR : tournamentSize incorrect"
			return
		elif (tourmanentSize ==1):
			return self.genomePool[ random.randint(0,len(self.genomePool))]
		actualSize = min ( tourmanentSize,len(self.genomePool))
		maxFitness = 0
		for i in range (actualSize):
			indexRandom = random.randint(0,len(self.genomePool) )
			
			if (maxFitness < self.fitnessPool[indexRandom]):
				greatessGenome = self.genomePool[indexRandom]
			self.genomePool.remove(indexRandom)
			self.fitnessPool.remove(indexRandom)
		return greatessGenome
		
		
		
	def equals(self, other):
		
		return  self.myGenome.equals (other.myGenome)
			
		
	def receiveComMessage(self, data) :
		sender = ""
		value = []
		if "senderHostname" in data.keys() :
			sender = data["senderHostname"]

			if "value" in data.keys() :
				value = data["value"]
				self.__listMessages.append((sender, value))
				self.genomePool.append(value[0])
				self.fitnessPool.append(value[1])
			else :
				self.mainLogger.error('SimulationTestCommunication - Receiving message from ' + str(sender) + ' without value data : ' + str(data))
		else :
			self.mainLogger.error('SimulationTestCommunication - Receiving message without sender : ' + str(data))
		
		"""FAIRE L'ENREGISTREMENT"""
		while len(self.__listMessages) > 0 :
				message = self.__listMessages.pop(0)
				self.mainLogger.debug('SimulationTestCommunication - Received ' + str(message[1]) + ' from ' + str(message[0]))




	def broadcast (self):
		try :
			
			if (self.__cptStep % self.__frequencyMess == 0) and ((self.__cptStep/self.__frequencyMess) < self.__maxMess) :
				recipientsList = ''

				for rpi in self.__listRpis :
					recipientsList += str(rpi) + ','
				self.sendMessage(recipients = recipientsList, value = (self.myGenome, self.fitness))
		except :
			self.mainLogger.critical('SimulationTestCommunication - Unexpected error' )


	def updateFitness(self) :
		Sk = 0
		for i in range (7):
			Sk = max (getSensorValue(i))
		getSensorValue(i)
		self.fitness = self.getTrasitiveAcceleration() * ( 1 - self.getAngularAceeleration() * (1- Sk/DISTANCE_MAX_VISION ))
		self.oldtransitifAcelleration = getAccelerometerValue(0)
		self.oldAngularAcelleration= getAccelerometerValue(1)
		
	def getTrasitiveAcceleration(self):
		return getAccelerometerValue(0) - self.oldtransitifAcelleration
		
	def getAngularAceeleration(self):
		return getAccelerometerValue(1) - self.oldAngularAcelleration	
		
"""		
main = SimulationVanillaEE (None, None)


start = time.time()
runTime = 100
#print in the terminal the name of each Aseba NOde


#GObject loop
print 'starting loop'
loop = gobject.MainLoop()
#call the callback of Braitenberg algorithm
handle = gobject.timeout_add (100, main.step()) #every 0.1 sec
loop.run()
"""