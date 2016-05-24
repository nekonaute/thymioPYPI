

import numpy as np
import random

import copy

class genome :
    
    def __init__(self, geneSize = 0,_genome = None ) :
        if (geneSize != 0):
            self.gene = np.zeros(geneSize)
            for i in range (geneSize) :
                self.gene[i]= -0.1 + random.random()*0.2
            self.gene[len(self.gene)/2 -1] *=1000 # based speed
            self.gene[len(self.gene)-1] *=1000 # based speed
        elif (_genome != None):
            self = copy.deepcopy(_genome)  
        
    def evaluationLeft(self, enter):
        result = 0
        for i in range (len(self.gene)/2):
            if (i< len(enter)):
                result += self.gene[i] * enter[i]
            else :
                result += self.gene[i]
        return result  
    
    def evaluationRight(self,enter):
        result = 0
        for i in range (len(self.gene)/2):
            if (i< len(enter)):
                result += self.gene[i+len(self.gene)/2] * enter[i]
            else :
                result += self.gene[i+len(self.gene)/2]
        return result 
    
    def MutationLinear(self,alpha,epsilon):
        copyGenome = genome (self)
        for i in range (alpha) :
            rand = random.randint(0, len(self.gene))
            copyGenome[rand] = copyGenome[rand] * (-1)**(random.randint(0,100)) *random.random() * epsilon
        return copyGenome 
        
    
    def MutationGaussian(self,sigma ):
        copyGenome = genome (self)
        for i in range (len(self.gene)) :
            copyGenome[i] = np.random.normal(copyGenome[i], sigma)
        return copyGenome 
        
    
    #obtain the size of the gene
    def getSize(self):
        return len(self.gene)
    
    #set the gene value to the position index
    def setGene(self, index,value):
        self.gene[index] = value
    
    #obtain the value of the index position
    def getGene(self, index):
        return self.gene[index]
    
    
    
    def equals(self, other):
        if (len(self.gene) != len(other.gene) ):
            return False
        for i in range ( len(self.gene)):
            if (self.gene[i] != other.gene[i]):
                return False
        return True
    
    def toString(self):
        s = ""
        for i in range (len(self.gene)):
            s += str(self.getGene(i)) +"|"
        s += "\n"
        return s
    
    
    
