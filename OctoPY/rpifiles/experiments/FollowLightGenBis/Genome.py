# -*- coding: utf-8 -*-

"""
Stage UPMC ISIR 2017
Encadrant : Nicolas Bredeche

@author Parham SHAMS

Classe Genome utilisée pour représenter le génome de l'algorithme génétique de suivi de lumière.
"""

import random
import math
import numpy as np
import copy

import Params

class Genome:
	
	def __init__(self, mainLogger, size=0, geneValue=[]) :
		self.logger = mainLogger
		
		if size==0:
			if geneValue==[]:
				self.logger.debug("Genome - init() : 0 sized gene created")
			else:								
				self.size=len(geneValue)
				self.gene=geneValue
		else:
			if geneValue!=[]:
				if len(geneValue)!=size:
					self.logger.debug("Genome - init() : size argument differs from the size of geneValue, size is set to len(geneValue)")
				else:
					self.size=size
					self.gene=geneValue
			else:
				# generation d'un genome de taille size avec genes compris entre -1 et 1
				self.gene = [-1+random.random()*2 for i in range(size)] 
				self.size=size
	
	def sigmoide(self,x):
		
		#return (1/(1+ math.exp(-2*x))) * Params.params.maxSpeedValue *2  - Params.params.maxSpeedValue
		
		try:
			a = (1/(1+ math.exp(-2*x))) * Params.params.maxSpeedValue *2  - Params.params.maxSpeedValue
			return a
		except OverflowError:
			if x>0:
				return 100000
			else:
				return -10000
		
	def evaluation(self, sensors):
		
		if len(sensors)!=self.size/2-1:
			self.logger.debug("Genome - evaluation() : number of sensors doesn't match with genome size")
			return (0,0)
			
		# initialisation avec les biais
		sum_g, sum_d = (self.gene[self.size/2-1], self.gene[-1])
		
		for i in range(self.size/2-1):		
			sum_g += sensors[i]*self.gene[i]
			sum_d += sensors[i]*self.gene[i+self.size/2]
					
		return (self.sigmoide(sum_g), self.sigmoide(sum_d))
		
		
	def mutationGaussienne(self,sigma):
		copyGenome = Genome(self.logger, geneValue = copy.deepcopy(self.gene))
		
		for i in range (len(self.gene)) :
			copyGenome.gene[i] = np.random.normal(copyGenome.gene[i], sigma)
			
		return copyGenome 		
		
		
		
		
