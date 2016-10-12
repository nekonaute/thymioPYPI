#!/usr/bin/env/python

import Simulation
import Params

import dbus
import dbus.mainloop.glib
import gobject
import time
#from ThymioFunctions import *
#from optparse import OptionParser

import genome
import vision
import random
import threading
import sys
import traceback



start = time.time()
runTime = 10
RESOURCES = 100
loop= gobject.MainLoop()
PROX_SENSORS_MAX_VALUE = 4500


class SimulationVanillaEE(Simulation.Simulation) :
	
	
	def __init__(self, controller, mainLogger) :
         Simulation.Simulation.__init__(self, controller, mainLogger)
         self.altern = 0
         self.i = 555555
         self.myGenome = genome.genome(7*2*3+2)# 7 sensor * 2 output * 3 type of thing to detect + 1 "control" value per output
         self.eye = vision.vision(self) #class with the technik of captation of the environnement
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
         mon_file = open ("log.txt","w")
         mon_file.write("log begin\n")
         mon_file.close()
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
#		self.tController.writeColorRequest([99,99,99])
         pass

	def postActions(self) :
         self.waitForControllerResponse()
         self.tController.writeMotorsSpeedRequest([0, 0])
         self.waitForControllerResponse()
         self.tController.writeColorRequest( [99, 99, 99])
#		setMotorSpeed(0, 0)
  

	def step(self) :
     
     
         """test to move the robot"""
#         try :
#             self.tController.readSensorsRequest()
#             self.waitForControllerResponse()
#             PSValues = self.tController.getPSValues()
#             noObstacle = True
#             for i in range(5) :
#                 if PSValues[i] > 0 :
#                     noObstacle = False
#                     break
#                 if noObstacle :
#                     # Probability to do a left a right turn
#                     rand = random.random()
#                     if rand < 0.5 :
#                         self.tController.writeMotorsSpeedRequest([200, 0])
#                     else :
#                         self.tController.writeMotorsSpeedRequest([0, 200])
#                         self.waitForControllerResponse()
#                         time.sleep(0.5)
#                         self.tController.writeMotorsSpeedRequest([200, 200])
#         except :
#             self.mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
#         self.waitForControllerResponse()
#         self.tController.writeColorRequest([0,0,0])
#         time.sleep(0.5)
         """test to write the reveived message in a file"""
#         self.tchatBetweenRobot()
#         self.evaluation()
#         mon_file = open ("log.txt","a")
#         mon_file.write(str(self.i)+ "\n")
#         mon_file.close()
#         self.i +=1
         """atern bleu and green"""
         if self.altern ==0 :
             self.waitForControllerResponse()
             self.tController.writeColorRequest([99,99,00])
#                 self.tController.writeMotorsSpeedRequest([10, 10])
             self.altern = 1
             time.sleep(0.5)
         elif self.altern == 1:
#                 self.tController.writeColorRequest([99,00,00])
             self.waitForControllerResponse()
             self.tController.writeColorRequest([0,99,99])
#                 self.tController.writeMotorsSpeedRequest([-10, -10])
             self.altern = 0
             time.sleep(0.5)
         """theoricalie change gradualy the color"""
#         if (self.i < 999999):
#             self.i += 1
#         else :
#             self.i = 0  
#         self.waitForControllerResponse()
#         self.tController.writeColorRequest([int (self.i/10000),int ((self.i%10000)/100),int ((self.i%100))])
#         time.sleep(0.2)  
         """ an other test to move the robot"""    
#         self.tController.writeColorRequest([00,99,00])
#         self.tController.writeMotorsSpeedRequest([200, 00])
#         print "1"
#         self.tController.writeColorRequest([99,00,00])
#         self.tController.writeMotorsSpeedRequest([0, 200])
#         print "2"
#         self.tController.writeColorRequest([0,00,99])
#         self.tController.writeMotorsSpeedRequest([200, 200])
#         print "3"
#         self.tController.writeColorRequest([99,99,99])
#         self.tController.writeMotorsSpeedRequest([0, 00])
#         print "4"
#         self.evaluation()
#         if time.time()-start < runTime:
                #	self.ticks +=1
                #	
                #	#if (self.alive):
                #	if( self.alive):
                #			
#                		self.evaluation()
                #	
                #		self.updateFitness()
                #
                #			print self.fitness
                #	
                #		self.resourcesManagement()
                #	
#             self.tchatBetweenRobot()
#             flash(white, white)
                #	
                #		self.evolution()
			
#             return True		
#        if time.time()-start>=runTime:
#    			setMotorSpeed(0, 0)
#    			print 'ending loop'
#    			loop.quit()
#    			return False

#    evaluate the environement and control the wheel
	def evaluation(self):
		entry = self.eye.updateVision()
		s = ""
		for i in range (len(entry)):
			s+= str(entry[i]) + "|"
# 		print s####################################################################################
		left = self.myGenome.evaluationLeft(entry) 
		right = self.myGenome.evaluationRight(entry) 
		print "left=" +str(left) + "  right = " + str(right)
		self.tController.writeMotorsSpeedRequest([left, right])
		#setMotorSpeed(0, 0)
		#setMotorSpeed(100, 100)
	
# manage the resources, if it had any in the enveronement, it will not be use
	def resourcesManagement(self):
		if (self.resources > 0):
			self.resources += -1 ;
		if (self.resources == 0):
			self.alive = False
	
 # this function is use to speak with other robot, you are free to change it
 # in this state, it will sens to all other robots is genome and is fitness
	def tchatBetweenRobot(self):
		self.broadcast()
		
# this function is use to evolve the robots when we considerate the genome pool and their associate fitness
  #you can change it, but it is not welcoming
	def evolution(self):
		if (self.ticks == self.generations):
			self.ticks = 0
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
				else:
					self.myGenome = child.MutationGaussian(self.sigma)
					self.resources = RESOURCES
					self.alive = 1
				self.genomePool = []
				self.fitnessPool = []
				self.fitness = 0
		
		
#	make a selection with the differents genomes in the genome pool
  #the tournamentSize define how many genome we take randomly ans then we selectionate the best of them
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
		
		
      #say if the genome of this agent is the same than an other
	def equals(self, other):
		
		return  self.myGenome.equals (other.myGenome)
			
   #function to receive message of other robots
	def receiveComMessage(self, data) :
		self.waitForControllerResponse()
		self.tController.writeColorRequest([50,0,50])
		time.sleep(1.5)
		sender = ""
		value = []
		if "senderHostname" in data.keys() :
			sender = data["senderHostname"]
			if "value" in data.keys():
                           self.waitForControllerResponse()
                           self.tController.writeColorRequest([00,0,00])
                           value = data["value"]
                           self.__listMessages.append((sender, value))
                           mon_file = open ("log.txt","a")
                           mon_file.write( "value"+ "\n")
                           mon_file.close()
#				self.genomePool.append(value[0])
#				self.fitnessPool.append(value[1])
			else :
				self.mainLogger.error('SimulationTestCommunication - Receiving message from ' + str(sender) + ' without value data : ' + str(data))
		else :
			self.mainLogger.error('SimulationTestCommunication - Receiving message without sender : ' + str(data))
		
#		"""FAIRE L'ENREGISTREMENT"""
#		while len(self.__listMessages) > 0 :
#				message = self.__listMessages.pop(0)
#				self.mainLogger.debug('SimulationTestCommunication - Received ' + str(message[1]) + ' from ' + str(message[0]))



#    boradcast his genome to all robots 
	def broadcast (self):
		try :
			
				recipientsList = ''

				for rpi in self.__listRpis :
					recipientsList += str(rpi) + ','
				self.sendMessage(recipients = recipientsList, value = "hello")
#				self.waitForControllerResponse()
#				self.tController.writeColorRequest([0,0,10])
#				time.sleep(0.5)
              
                        
		except :
			self.mainLogger.critical('Test Communication - Unexpected error' )

#update his fitness we what he see
	def updateFitness(self) :
		Sk = 0
		for i in range (7):
			Sk = max (getSensorValue(i))
		getSensorValue(i)
		self.fitness = self.getTrasitiveAcceleration() * ( 1 - self.getAngularAceeleration() * (1- Sk/DISTANCE_MAX_VISION ))
		self.oldtransitifAcelleration = getAccelerometerValue(0)
		self.oldAngularAcelleration= getAccelerometerValue(1)
		
  #do i have really to comment ?
	def getTrasitiveAcceleration(self):
		return getAccelerometerValue(0) - self.oldtransitifAcelleration
		
  #refer to the comment of getTransitiveAcceleration
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
