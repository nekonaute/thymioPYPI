#!/usr/bin/env/python

import Simulation
import Params
import copy


class data() :
    
   def __init__(self,myController):
         """ record of log """
         self.recordGenome= []
         self.recordFitness= []
         self.recordReservoirSize= []
         self.recordAgentAlive= []
         self.myController = myController
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/nbGenome.csv","w")
         mon_file.write("number of Genome\n")
         mon_file.close()
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/fitness.csv","w")
         mon_file.write("median fitness\n")
         mon_file.close()
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/reservoirSize.csv","w")
         mon_file.write("median reservoir size\n")
         mon_file.close()
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/fitnessMax.csv","w")
         mon_file.write("max fitness\n")
         mon_file.close()
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/reservoirSizeMax.csv","w")
         mon_file.write("max reservoir size\n")
         mon_file.close()
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/nbAlive.csv","w")
         mon_file.write("number of agent active\n")
         mon_file.close()
   
   
            
   def setFitness(self,fitness) :
        self.recordFitness = fitness
        
   def setGenome(self,Genome) :
        self.recordGenome = Genome
        
   def setAgentAlive(self,AgentAlive) :
        self.recordAgentAlive = AgentAlive
        
   def setReservoirSize(self,ReservoirSize) :
        self.recordReservoirSize = ReservoirSize
        
   def setAll(self,arrayFitness, arrayGenome,arrayAgentAlive= [],arrayReservoirSize=[]):
       self.setFitness(arrayFitness)
       self.setGenome(arrayGenome)
       self.setAgentAlive(arrayAgentAlive)
       self.setReservoirSize(arrayReservoirSize)
       
       
   def save(self):
         
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/nbGenome.csv","a")
         mon_file.write(str(self.countGenome(self.recordGenome))+";")
         mon_file.close()
         fitnessSort = self.sort (self.recordFitness)
         median = self.getMedian(fitnessSort)
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/fitness.csv","a")
         mon_file.write(str(median)+";")
         mon_file.close()
         maxi =fitnessSort[len(fitnessSort)-1]
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/fitnessMax.csv","a")
         mon_file.write(str(maxi)+";")
         mon_file.close()
         mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/nbAlive.csv","a")
         mon_file.write(str(self.countAlive(self.recordAgentAlive))+";")
         mon_file.close()
         if self.myController.actualGeneration >= self.myController.numberOfGeneration:
             mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/nbGenome.csv","a")
             mon_file.write("\n")
             mon_file.close()
             mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/fitness.csv","a")
             mon_file.write("\n")
             mon_file.close()
             mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/fitnessMax.csv","a")
             mon_file.write("\n")
             mon_file.close()
             mon_file = open ("/home/pi/dev/thymioPYPI/OctoPY/rpifiles/VanillaEE/log/nbAlive.csv","a")
             mon_file.write("\n")
             mon_file.close()


#all in one  (and not one in all)         
   def update(self,arrayFitness, arrayGenome,arrayAgentAlive= [],arrayReservoirSize=[]):    
       self.setAll(arrayFitness, arrayGenome,arrayAgentAlive,arrayReservoirSize)
       self.save()
       
       
       
       
       
       
       
   # sort the array given and return the result     
   def sort (self, array):
       copied = copy.deepcopy(array)
       result = []
       while len(copied) != 0:
           mini = copied[0]
           argmin =0
           for j in range (len(copied)):
               if (mini > copied[j]):
                   mini = copied[j]
                   argmin = j
           result.append(copied[argmin])
           copied.pop(argmin)
       return result
     
    
   #give the median of the array which is sort before    
   def getMedian(self, arraySort):
       return arraySort[int(len(arraySort)/2)]
       
       
   def countAlive(self,array):
        nbAlive=0
        for i in range (len(array)):
            nbAlive += array[i]
        return nbAlive               
               
   def countGenome(self, arrayGenome):
       nbgenome =0
       arrayExistant=[]
       for i in range (len(arrayGenome)):
           exist = False
           for j in arrayExistant :
               if (arrayGenome[i].getID() == j):
                   exist = True
           if ( not exist):
               nbgenome +=1
               arrayExistant.append(arrayGenome[i].getID())
       return nbgenome
       
       
       
       
            
            
            