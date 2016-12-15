#!/usr/bin/env/python

import Simulation
import Params

import sys
import traceback
import time


class SimulationTestCommunication(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		listRpis = Params.params.list_rpis
		self.__listRpis = listRpis.split(',')
		self.__frequencyMess = int(Params.params.frequency_mess)
		self.__maxMess = int(Params.params.max_mess)

		self.__listMessages = list()
		self.__cptStep = 0

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		try :
			while len(self.__listMessages) > 0 :
				message = self.__listMessages.pop(0)
				self.mainLogger.debug('SimulationTestCommunication - Received ' + str(message[1]) + ' from ' + str(message[0]))

			if (self.__cptStep % self.__frequencyMess == 0) and (self.__cptStep < self.__maxMess) :
				recipientsList = ''

				for rpi in self.__listRpis :
					recipientsList += str(rpi) + ','
				self.sendMessage(recipients = recipientsList, value = self.__cptStep)

			self.__cptStep += 1
			time.sleep(0.5)
		except :
			self.mainLogger.critical('SimulationTestCommunication - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

	def receiveComMessage(self, data) :
		if "senderHostname" in data.keys() :
			sender = data["senderHostname"]

			if "value" in data.keys() :
				value = data["value"]
				self.__listMessages.append((sender, value))
			else :
				self.mainLogger.error('SimulationTestCommunication - Receiving message from ' + str(sender) + ' without value data : ' + str(data))
		else :
			self.mainLogger.error('SimulationTestCommunication - Receiving message without sender : ' + str(data))