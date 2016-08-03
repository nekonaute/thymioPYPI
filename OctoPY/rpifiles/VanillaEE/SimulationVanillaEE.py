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
import enregisterData
import random
import threading
import sys
import traceback



start = time.time()
runTime = 10
RESOURCES = 100
loop= gobject.MainLoop()
PROX_SENSORS_MAX_VALUE = 4500
MAX_SPEED_VALUE = 200


class SimulationVanillaEE(Simulation.Simulation) :
	
	
	def __init__(self, controller, mainLogger) :
              
         Simulation.Simulation.__init__(self, controller, mainLogger)
     
         myName = Params.params.myName
         self.myName = myName #name of the agent  
         
         self.data = enregisterData.data(self)

         self.left = 0  #speed of the left wheel
         self.right = 0 # speed of the right wheel
         self.myGenome = genome.genome(owner= self.myName,geneSize=7*2+2)# 7 sensor * 2 output * 3 type of thing to detect + 1 "control" value per output
         self.eye = vision.vision(7,self) #class with the technik of captation of the environnement
#         self.resources = RESOURCES; # find a way to initiate all of that
         self.fitness =0 # the fitness of the agent
         self.fitnessWindow = []  #sliding window for the fitness
         self.genomePool= [[]] #stock the genome of the other robots
         self.fitnessPool= [[]] #stock the fitness of the other robots
         self.alive = True # if active or not
         self.ticks = 0  #number of step after the change of generation
         
         
         windowsize  = Params.params.windowsize 
         self.fitnessWindowSize = windowsize #the window for the fitness have a size. This size
         
         tournamentSize = Params.params.tournamentSize
         self.numberOfTheTournament = tournamentSize #size of the tounrament (for the selection)
         
         
         stepBeforeNextGeneration = Params.params.stepBeforeNextGeneration
         self.stepBeforeNextGenerations = stepBeforeNextGeneration #time before next generation
         
         sigma = Params.params.sigma
         self.sigma = sigma  # parameter of mutation
         
         nbAgent= Params.params.nbAgent
         self.nbAgent = nbAgent #know hom many agents the experiment count. Use to evolve
         
         nbRun = Params.params.nbRun
         self.numberOfRuns = nbRun  # number of run, after this , it stop
         self.actualRuns = 0
         
         nbGeneration = Params.params.nbGeneration
         self.numberOfGeneration = nbGeneration  # number of run, after this , it stop
         self.actualGeneration = 0  #the agent evovle by generation. We can know which is his generation
      
         
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/log/logVanillaEE.txt","w") #useless ?
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
         """ record of log """
         self.recordGenome= [self.numberOfRuns,0]
         self.recordFitness= [self.numberOfRuns,0]
         self.recordReservoirSize= [self.numberOfRuns,0]
         self.recordAgentAlive= [self.numberOfRuns,0]
#         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/SimulationVanillaEE/log/nbGenome.csv","w")
#         mon_file.write("number of Genome\n")
#         mon_file.close()
#         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/SimulationVanillaEE/log/fitness.csv","w")
#         mon_file.write("median fitness\n")
#         mon_file.close()
#         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/SimulationVanillaEE/log/reservoirSize.csv","w")
#         mon_file.write("median reservoir size\n")
#         mon_file.close()
#         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/SimulationVanillaEE/log/fitnessMax.csv","w")
#         mon_file.write("max fitness\n")
#         mon_file.close()
#         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/SimulationVanillaEE/log/reservoirSizeMax.csv","w")
#         mon_file.write("max reservoir size\n")
#         mon_file.close()
#         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/SimulationVanillaEE/log/nbAlive.csv","w")
#         mon_file.write("number of agent active\n")
#         mon_file.close()
         self.timeForEvolution= threading.Event()
         
         

	def preActions(self) :
         for i in range (4):
             self.tController.writeColorRequest( [99, 99, 99])
             self.waitForControllerResponse()
             time.sleep(0.1)
             self.tController.writeColorRequest([00,0,00])
             self.waitForControllerResponse()
             time.sleep(0.1)

	def postActions(self) :
         
         self.tController.writeMotorsSpeedRequest([0, 0])
         self.waitForControllerResponse()
         self.tController.writeColorRequest( [99, 99, 99])
         self.waitForControllerResponse()

  

	def step(self) :
          self.ticks +=1
          self.evaluation()
          if (self.ticks < self.stepBeforeNextGenerations):
              self.updateFitness() #evalute the fitness anly for the time of one generation then stop
#          self.mainLogger.debug("fitness = " + str(self.fitness))
          if (self.ticks >= self.stepBeforeNextGenerations): #END OF A GENERATION
              if (self.ticks % self.stepBeforeNextGenerations ==0):
                  self.broadcast() #between each tme of one generation , broadcast the genome
              if (len (self.genomePool) > self.actualGeneration and len(self.genomePool[self.actualGeneration]) >= self.nbAgent):
                  self.timeForEvolution.set()
              if (self.timeForEvolution.is_set()):
                  self.data.update(self.fitnessPool[self.actualGeneration],self.genomePool[self.actualGeneration])
                  self.mainLogger.debug("My OLD GENOME IS:" + self.myGenome.toString())
                  self.evolution()
                  self.mainLogger.debug("My NEW GENOME IS:" + self.myGenome.toString())
                  self.timeForEvolution.clear()
                  self.ticks = 0;
                  self.gestionExperiment()      
          time.sleep(0.2) #whait between 2 steps
              
          
	"""SPECFIC FUNCTION OF VANILLA EMBODIED EVOLUTION """    
  

#    evaluate the environement and control the wheel
	def evaluation(self):
#		self.mainLogger.debug(self.myGenome.toString())
		entry = self.eye.updateVision()
#		s = ""
#		for i in range (len(entry)):
#			s+= str(entry[i]) + "|"
#		self.mainLogger.debug(s)
# 		print s####################################################################################
		self.left = self.myGenome.evaluationLeft(entry) 
		self.right = self.myGenome.evaluationRight(entry) 
#		print "left=" +str(self.left) + "  right = " + str(self.right)
#		self.mainLogger.debug("vitesse gauche =" + str(self.left) + "  vitesse droite =" + str(self.right))
		self.tController.writeMotorsSpeedRequest([self.left, self.right])
		self.waitForControllerResponse()
	

	
 # this function is use to speak with other robot, you are free to change it
 # in this state, it will sens to all other robots is genome and is fitness
	def tchatBetweenRobot(self):
		self.broadcast()
		
# this function is use to evolve the robots when we considerate the genome pool and their associate fitness
  #you can change it, but it is not welcoming
	def evolution(self):
		self.tController.writeColorRequest([00,99,00])
		self.waitForControllerResponse()
		time.sleep(0.5)
		self.tController.writeColorRequest([00,0,00])
		self.waitForControllerResponse()
		time.sleep(0.5)
		child = genome.genome(self.myName)
		child = self.tournament(self.numberOfTheTournament)
		if ((self.myGenome.equals(child))):
                  self.fitness = 0
#                  self.resourcesManagement()
                  self.alive = 0				 
		else:
                  self.myGenome = child.MutationGaussian(self.sigma)
#				self.resources = RESOURCES
                  self.alive = 1
#			self.genomePool = []
#			self.fitnessPool = []
		self.fitness = 0
		self.ticks = 0
		self.fitnessWindow = []
			
# manage the resources, if it had any in the enveronement, it will not be use
	def resourcesManagement(self):
		if (self.resources > 0):
			self.resources += -1 ;
		if (self.resources == 0):
			self.alive = False		
		
#	make a selection with the differents genomes in the genome pool
  #the tournamentSize define how many genome we take randomly ans then we selectionate the best of them
	def tournament(self,tourmanentSize):
		greatessGenome =self.myGenome

		if tourmanentSize <= 0 :
			self.mainLogger.error( "ERROR : tournamentSize incorrect")
			return
		elif (tourmanentSize ==1):
			return self.genomePool[self.actualGeneration][ random.randint(0,len(self.genomePool[self.actualGeneration]))]
		self.mainLogger.debug( "actual generation is " +str(self.actualGeneration))		
		actualSize = min ( tourmanentSize,len(self.genomePool[self.actualGeneration]))
		maxFitness = 0
#		self.mainLogger.debug( "size for the tounament is " +str(actualSize))
		for i in range (actualSize):# try the the number of enable genome
			indexRandom = random.randint(0,len(self.genomePool[self.actualGeneration])-1 )
			
			if (maxFitness < self.fitnessPool[self.actualGeneration][indexRandom]): # if the genome is the best a this moment , we keep it 
				greatessGenome = self.genomePool[self.actualGeneration][indexRandom]
				maxFitness = self.fitnessPool[self.actualGeneration][indexRandom]
			self.genomePool[self.actualGeneration].pop(indexRandom) # erase those was already tested
			self.fitnessPool[self.actualGeneration].pop(indexRandom) #same for the fitness (already tested)
		return greatessGenome  # the best genome among those random
		
  
  
  
  
	def gestionExperiment(self):
		if self.actualGeneration < self.numberOfGeneration:
                  self.actualGeneration +=1
		else :
                  if (self.actualRuns < self.numberOfRuns):
                      self.actualRuns +=1
                      self.actualGeneration = 0
                      self.reset()
                      for i in range (120):
                              self.stepBrainterberg()
                              self.tController.writeColorRequest( [99, 00, 00])
                              self.waitForControllerResponse()
                              self.tController.writeColorRequest( [0, 99, 99])
                              self.waitForControllerResponse()
                      for i in range (4):
                          self.tController.writeColorRequest( [99, 00, 00])
                          self.waitForControllerResponse()
                          time.sleep(0.3)
                          self.tController.writeColorRequest([00,00,99])
                          self.waitForControllerResponse()
                          time.sleep(0.3)
                          self.tController.writeColorRequest([00,0,00])
                          self.waitForControllerResponse()
                          
                  else :
                      self.stop()
                      
	def reset(self):
         self.left = 0  #speed of the left wheel
         self.right = 0 # speed of the right wheel
         self.myGenome = genome.genome(owner= self.myName,geneSize=7*2+2)# 7 sensor * 2 output * 3 type of thing to detect + 1 "control" value per output
         self.eye = vision.vision(7,self) #class with the technik of captation of the environnement
#         self.resources = RESOURCES; # find a way to initiate all of that
         self.fitness =0 # the fitness of the agent
         self.fitnessWindow = []  #sliding window for the fitness
         self.genomePool= [[]] #stock the genome of the other robots
         self.fitnessPool= [[]] #stock the fitness of the other robots
         self.alive = True # if active or not
         self.ticks = 0  #number of step after the change of generation
		

			



#update his fitness we what he see
	def updateFitness(self) :
		Sk = 0
		self.tController.readSensorsRequest()
		self.waitForControllerResponse()
		proxSensors = self.tController.getPSValues()
		for i in xrange (7):
			Sk = max(Sk,  proxSensors[i])
		self.fitness = self.updateFitnessWindow((self.getTrasitiveAcceleration()/ (2*MAX_SPEED_VALUE)) * (1- self.getAngularAceeleration()/ (2*MAX_SPEED_VALUE ))* (1- Sk/PROX_SENSORS_MAX_VALUE ))
		



	def updateFitnessWindow(self, value):
          if( len(self.fitnessWindow)>= self.fitnessWindowSize):
              self.fitnessWindow.pop(0)
          self.fitnessWindow.append(value)
          result = 0
          for i in range (len(self.fitnessWindow)):
              result += self.fitnessWindow[i]
          return result /(len(self.fitnessWindow))	

      #say if the genome of this agent is the same than an other
	def equals(self, other):
		return  self.myGenome.equals (other.myGenome)
  
  #do i really have  to comment ?
	def getTrasitiveAcceleration(self):
		return abs(self.left + self.right) 
		
  #refer to the comment of getTransitiveAcceleration
	def getAngularAceeleration(self):
		return abs(self.left - self.right)
           
         
	"""MESSAGE"""       

   #function to receive message of other robots
	def receiveComMessage(self, data) :
		
		sender = ""
		value = []
		if "senderHostname" in data.keys() :
			sender = data["senderHostname"]
			if "value" in data.keys():
                           value = data["value"]
                           self.__listMessages.append((sender, value))
#                           mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/log/logVanillaEE.txt","a")
#                           mon_file.write( value+ "\n")
#                           mon_file.close()
                           self.tController.writeColorRequest([50,0,99])
                           self.waitForControllerResponse()
                           time.sleep(0.5)
                           self.tController.writeColorRequest([00,0,00])
                           self.waitForControllerResponse()
                           time.sleep(0.5)
                           self.mainLogger.debug("RECEIVED MESSAGE FROM: " + str(sender)+ "\n MESSAGE :" + str(value))#+ value)
                           """ processing the DATA"""
                           valuesplit = value.split(",")
                           if (valuesplit[0] == "vanillaEE"):
#                               self.mainLogger.debug("ADD OF THE LAST GENOME")
                               if(len(self.genomePool) <= int(valuesplit[3])):
                                   self.genomePool.append([])
                                   self.fitnessPool.append([])
                               owner, gene = self.stringtoArray(valuesplit[1])
                               self.genomePool[int(valuesplit[3])].append(genome.genome(owner = owner, gene =gene))
                               self.fitnessPool[int(valuesplit[3])].append(float(valuesplit[2]))
                               
                               
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
				self.sendMessage(recipients = recipientsList, value = ("vanillaEE,"+self.myGenome.toString() +","+str(self.fitness) +","+str(self.actualGeneration)))              
		except :
				self.mainLogger.critical('Test Communication - Unexpected error' )


		
  
  #transform a string s in an array which is a genome (noramally)
	def stringtoArray(self, s):
		result = []
		ss =s.split("$")
		owner = ss[1]
		ssplit = ss[0].split("|")
		for value in ssplit :
#                  self.mainLogger.debug("value : "+ value)
                  result.append(float (value))
		return owner,result
  
  
  
  
  
  
	""" BRAINTENBERG"""

	def Braitenberg(self, proxSensors, avoidance) :
		if not avoidance :
			leftWheel = [-0.1, -0.05, -0.001, 0.06, 0.15]
			rightWheel = [0.12, 0.07, -0.002, -0.055, -0.11]
		else :
			leftWheel = [0.1, 0.05, 0.001, -0.06, -0.15]
			rightWheel = [-0.12, -0.07, 0.002, 0.055, 0.11]

		# Braitenberg algorithm
		totalLeft = 0
		totalRight = 0
		for i in range(5) :
			if not avoidance :
				value = 0.0

				if proxSensors[i] > 0.0 :
					value = PROX_SENSORS_MAX_VALUE - proxSensors[i]

					if value < 0.0 :
						value = 0.0

				# self.log(str(i) + "/" + str(proxSensors[i]) + "/" + str(value))
				totalLeft = totalLeft + (value * leftWheel[i])
				totalRight = totalRight + (value * rightWheel[i])
			else :
				totalLeft = totalLeft + (proxSensors[i] * leftWheel[i])
				totalRight = totalRight + (proxSensors[i] * rightWheel[i])

		# Add a constant speed
		# if not avoidance :
		# 	totalRight = totalRight + 150
		# 	totalLeft = totalLeft + 150
		# else :
		totalRight = totalRight + 200
		totalLeft = totalLeft + 200

		self.tController.writeMotorsSpeedRequest([totalLeft, totalRight])

		return True

	def stepBrainterberg(self) :
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

				if rand < 0.66 :
					rand = random.random()

					if rand < 0.33 :
						self.tController.writeMotorsSpeedRequest([200, 0])
					elif rand< 0.66 :
						self.tController.writeMotorsSpeedRequest([0, 200])
					else :
						self.tController.writeMotorsSpeedRequest([500, 500])
					self.waitForControllerResponse()
					

				
			else :
				self.Braitenberg(PSValues, True)
			time.sleep(0.5)
		except :
			self.mainLogger.critical('SimulationDefault - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
  
  
  
  
  
  
  
  
  
  
		
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
