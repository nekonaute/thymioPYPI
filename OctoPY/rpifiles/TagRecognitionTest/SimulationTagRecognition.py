#!/usr/bin/env/python

import Simulation
import Params
import TagRecognition.mainTagRecognition as tr

ROBOTS_ID = {
					"1" : pi3no01,
					"2" : pi3no02,
					"3" : pi3no03,
					"4" : pi3no04,
					"5" : pi3no05,
					"6" : pi3no06,
					"7" : pi3no07,
					"8" : pi3no08,
					"9" : pi3no09
}

class SimulationTagRecognitionTest(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)
		self.tagFinder = tr.mainTagRecognition(self.mainLogger)

	def preActions(self) :
		pass

	def postActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])

	def step(self) :
		results = self.tagFinder()

		# Analysis of results
		if len(results) > 0 :
			self.log("I saw {}".format(results))

			recipientsList = ''
			for robot in results :
				if str(robot[0]) in ROBOTS_ID.keys() :
					recipientsList += ROBOTS_ID[str(robot[0])] + ','

			self.sendMessage(recipients = recipientsList, value = "Hi !")


	def receiveComMessage(self, data) :
		if "senderHostname" in data.keys() :
			sender = data["senderHostname"]

			if "value" in data.keys() :
				value = data["value"]
				self.mainLogger.debug('SimulationTestCommunication - Received ' + str(value) + ' from ' + str(sender))
			else :
				self.mainLogger.error('SimulationTestCommunication - Receiving message from ' + str(sender) + ' without value data : ' + str(data))
		else :
			self.mainLogger.error('SimulationTestCommunication - Receiving message without sender : ' + str(data))