

import numpy as np
import random
import math
import copy

MAX_SPEED_VALUE = 200

class genome :
    
    def __init__(self,owner="", geneSize = 0, gene = [] ) :
        self.owner = owner
        if (geneSize != 0):
            self.gene = np.zeros(geneSize)
            for i in range (geneSize) :
                self.gene[i]= (-1 + random.random()*2) * 5
#            self.gene[len(self.gene)/2 -1] *=100 # based speed
#            self.gene[len(self.gene)-1] *=100 # based speed
        elif (gene != []):
            self.gene = gene 
        
    def evaluationLeft(self, enter):
        result = 0
        for i in range (len(self.gene)/2 ):
            if (i< len(enter)):
                result += self.gene[i] * enter[i]
            else :
                result += self.gene[i]
        return self.fonctionActivation(result)  
    
    def evaluationRight(self,enter):
        result = 0
        genomeSize =len(self.gene)/2
        for i in range (genomeSize ):
            if (i< len(enter)):
                result += self.gene[i+genomeSize] * enter[i]
            else :
                result += self.gene[i+genomeSize]
        return self.fonctionActivation(result) 
        
        
        
    def fonctionActivation(self,x):
        result = (1/(1+ math.exp(-x))) * MAX_SPEED_VALUE *2  - MAX_SPEED_VALUE
        if result > MAX_SPEED_VALUE:
            result = MAX_SPEED_VALUE
        if (result < -1* MAX_SPEED_VALUE):
            result = -1 * MAX_SPEED_VALUE
        return result
    
    def MutationLinear(self,alpha,epsilon):
        copyGenome = genome(owner= self.owner ,gene= copy.deepcopy(self.gene))
        for i in range (alpha) :
            rand = random.randint(0, len(self.gene))
            copyGenome[rand] = copyGenome[rand] * (-1)**(random.randint(0,100)) *random.random() * epsilon
        return copyGenome 
        
    
    def MutationGaussian(self,sigma ):
        copyGenome = genome(owner= self.owner ,gene= copy.deepcopy(self.gene))
        for i in range (len(self.gene)) :
            copyGenome.setGene(i, np.random.normal(copyGenome.getGene(i), sigma))
        return copyGenome 
        
    
    #obtain the size of the gene
    def getSize(self):
        return len(self.gene)
    
    #set the gene value to the position index
    def setGene(self, index,value):
        self.gene[index] = value
        
    def getID(self):
        return self.owner
        
     #replace the gene by the gene given in entry   
    def setAllGenes(self,genes ):
        self.gene = genes
    
    #obtain the value of the index position
    def getGene(self, index):
        return self.gene[index]
    
    
    
    def equals(self, other):
        if (len(self.gene) != other.getSize() ):
            return False
        for i in range ( len(self.gene)):
            if (self.gene[i] != other.getGene(i)):
                return False
        return True
    
    def toString(self):
        s = ""
        for i in range (len(self.gene)-1):
            s += str(self.getGene(i)) +"|"
        s += str(self.getGene(len(self.gene) -1))
        s+= "$"+str(self.owner)
        return s
        
        
    
    
    
