import numpy as np

import dbus
import dbus.mainloop.glib
import gobject
import time
from ThymioFunctions import *
from optparse import OptionParser


DISTANCE_MAX_VISION = 4500

class vision :
	
	
	def __init__(self):
		"""must detect separatly the robot [0,6] , the resources [7,13] and the other obstacles [14,20]"""
		self.enter =np.zeros(7*3) 
	
	
	#Fonction who must update the enter array and return it
	def updateVision(self):
		
		""" DO SOMETHING (but not enough yet)"""
		for i in xrange (7):
			self.enter[i] = getSensorValue(i)
			self.enter[i+7] = getSensorValue(i)
			self.enter[i+14] = getSensorValue(i)
			
		return self.enter
		