import numpy as np

import dbus
import dbus.mainloop.glib
import gobject
import time
#from ThymioFunctions import *
from optparse import OptionParser
import Simulation


DISTANCE_MAX_VISION = 4500
PROX_SENSORS_MAX_VALUE = 4500

class vision :
	
	
	def __init__(self,size, controller):
		"""must detect separatly the robot [0,6] , the resources [7,13] and the other obstacles [14,20]"""
		self.enter =np.zeros(size) 
		self.controller = controller
	
	
	#Fonction who must update the enter array and return it
	def updateVisionOld(self):
		
		""" DO SOMETHING (but not enough yet)"""
#		self.controller.waitForControllerResponse()
		self.controller.tController.readSensorsRequest()
		self.controller.waitForControllerResponse()
		proxSensors = self.controller.tController.getPSValues()
		for i in xrange (7):
			self.enter[i] = PROX_SENSORS_MAX_VALUE - proxSensors[i]
			self.enter[i+7] = PROX_SENSORS_MAX_VALUE - proxSensors[i]
			self.enter[i+14] = PROX_SENSORS_MAX_VALUE - proxSensors[i]
			
		return self.enter
		
  
	def updateVision(self):
#		self.controller.waitForControllerResponse()
		self.controller.tController.readSensorsRequest()
		self.controller.waitForControllerResponse()
		proxSensors = self.controller.tController.getPSValues()
		self.enter= [0,0,0,0,0,0,0]
		for i in xrange (7):
			self.enter[i] = proxSensors[i]/ DISTANCE_MAX_VISION
			
		return self.enter