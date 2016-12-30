# -*- coding: utf-8 -*-
import time
import glib, gobject
import dbus, dbus.mainloop.glib
import os
import threading
import traceback
import sys

import Simulation
import Params

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
AESL_PATH = os.path.join(CURRENT_FILE_PATH, ('asebaCommands.aesl'))

# Requests from the simulation
class MessageRequest() :
	NONE = -1

	# Read requests
	SENSORS, GROUND, STOP, MOTORSREAD = range(0, 4)

	# Write requests
	MOTORS, COLOR, SOUND = range(10, 13)

	KILL = 99


class ThymioController(threading.Thread):
	def __init__(self, simulation, mainLogger):
		threading.Thread.__init__(self)
		self.__simulation = simulation
		self.__mainLogger = mainLogger

		self.__performActionReq = threading.Condition()
		# self.__request = MessageRequest.NONE
		self.__request = []

		self.__stop = threading.Event()

		self.daemon = True

		self.__psValue = [0,0,0,0,0,0,0]
		self.__psGroundAmbiantSensors = [0,0]
		self.__psGroundReflectedSensors = [0,0]
		self.__psGroundDeltaSensors = [0,0]
		self.__motorspeed = [0,0]
		self.__color = [0,0,0]
		self.__sound = [0,0]


		# Init the main loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		# Get stub of the Aseba network
		bus = dbus.SessionBus()
		# Create Aseba network 
		asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')
		self.__asebaNetwork = dbus.Interface(asebaNetworkObject, dbus_interface='ch.epfl.mobots.AsebaNetwork')
		# self.__mainLogger.debug('Aseba nodes: ' + str(self.__asebaNetwork.GetNodesList()))
		# Load the aesl file
		self.__asebaNetwork.LoadScripts(AESL_PATH, reply_handler=self.__dbusEventReply, error_handler=self.__dbusError)
		# Schedules first run of the controller
		glib.idle_add(self.__execute)


	def __dbusError(self, e):
		# there was an error on D-Bus, stop loop
		self.__mainLogger.critical('Error in ThymioController: ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
		self.__mainLogger.critical('dbus error: %s' % str(e) + "\nNow sleeping for 1 second and retrying...")
		time.sleep(1)
		raise Exception("dbus error")
		# self.__loop.quit()

	def __dbusEventReply(self):
		# correct replay on D-Bus, ignore
		pass

	def __dbusSendEventName(self, eventName, params):
		ok = False
		while not ok:
			try:
				self.__asebaNetwork.SendEventName(eventName, params, reply_handler=self.__dbusEventReply, error_handler=self.__dbusError)
				ok = True
			except:
				ok = False

	def __dbusGetVariable(self, varName, replyHandler):
		ok = False
		while not ok:
			try:
				self.__asebaNetwork.GetVariable("thymio-II", varName, reply_handler=replyHandler, error_handler=self.__dbusError) 
				ok = True
			except:
				ok = False
	
	def __dbusSetMotorspeed(self):
		self.__dbusSendEventName("SetSpeed", self.__motorspeed)

	def __dbusSetColor(self):
		self.__dbusSendEventName("SetColor", self.__color)

	def __dbusSetSound(self):
		self.__dbusSendEventName("SetSound", self.__sound)
	
	def __dbusGetProxSensorsReply(self, r):
		self.__psValue = r

	def __dbusGetProxSensors(self):
		self.__dbusGetVariable("prox.horizontal", self.__dbusGetProxSensorsReply)

	def __dbusGetGroundAmbiantReply(self, r):
		self.__psGroundAmbiantSensors = r

	def __dbusGetGroundReflectedReply(self, r):
		self.__psGroundReflectedSensors = r

	def __dbusGetGroundDeltaReply(self, r):
		self.__psGroundDeltaSensors = r	

	def __dbusGetGroundSensors(self):
		self.__dbusGetVariable("prox.ground.ambiant", self.__dbusGetGroundAmbiantReply)
		self.__dbusGetVariable("prox.ground.reflected", self.__dbusGetGroundReflectedReply)
		self.__dbusGetVariable("prox.ground.delta", self.__dbusGetGroundDeltaReply)

	def __dbusGetMotorSpeedLeftReply(self, r) :
		self.__motorspeed[0] = int(r)

	def __dbusGetMotorSpeedRightReply(self, r) :
		self.__motorspeed[1] = int(r)

	def __dbusGetMotorSpeed(self):
		self.__dbusGetVariable("motor.left.speed", self.__dbusGetMotorSpeedLeftReply)
		self.__dbusGetVariable("motor.right.speed", self.__dbusGetMotorSpeedRightReply)

	def __execute(self):
		# Notifying that simulation has been set
		self.__simulation.thymioControllerPerformedAction()

		try :
			with self.__performActionReq:
				# Wait for requests:
				while len(self.__request) == 0 and not self.__stop.isSet() :
					self.__performActionReq.wait()

				while len(self.__request) :
					request = self.__request.pop(0)
					# self.__mainLogger.debug("Request : " + str(request))

					if request == MessageRequest.SENSORS :
						# Read sensor values
						self.__dbusGetProxSensors()
					elif request == MessageRequest.GROUND :
						# Read ground sensor values
						self.__dbusGetGroundSensors()
					elif request == MessageRequest.MOTORS :
						# Write motorspeed
						self.__dbusSetMotorspeed() # IF COMMENTED: wheels don't move
					elif request == MessageRequest.MOTORSREAD :
						# Read motorspeed
						self.__dbusGetMotorSpeed()
					elif request == MessageRequest.COLOR :
						self.__dbusSetColor()
					elif request == MessageRequest.SOUND :
						self.__dbusSetSound()
					elif request == MessageRequest.STOP :
						# Stop Thymio
						self.__stopThymio()

					# Notifying that simulation has been set
					self.__simulation.thymioControllerPerformedAction()

				# while self.__request == MessageRequest.NONE and not self.__stop.isSet() :
				# 	self.__performActionReq.wait()

				# self.__mainLogger.debug("Request : " + str(self.__request))

				# if self.__request == MessageRequest.SENSORS :
				# 	# Read sensor values
				# 	self.__dbusGetProxSensors()
				# elif self.__request == MessageRequest.GROUND :
				# 	# Read ground sensor values
				# 	self.__dbusGetGroundSensors()
				# elif self.__request == MessageRequest.MOTORS :
				# 	# Write motorspeed
				# 	self.__dbusSetMotorspeed() # IF COMMENTED: wheels don't move
				# elif self.__request == MessageRequest.MOTORSREAD :
				# 	# Read motorspeed
				# 	self.__dbusGetMotorSpeed()
				# elif self.__request == MessageRequest.COLOR :
				# 	self.__dbusSetColor()
				# elif self.__request == MessageRequest.SOUND :
				# 	self.__dbusSetSound()
				# elif self.__request == MessageRequest.STOP :
				# 	# Stop Thymio
				# 	self.__stopThymio()

				# self.__request = MessageRequest.NONE

				# # Notifying that simulation has been set
				# self.__simulation.thymioControllerPerformedAction()
		except :
			self.__mainLogger.critical('ThymioController - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

		if self.__stop.isSet() :
			self.killController()
			return False
		else :
			return True

	def readSensorsRequest(self):
		with self.__performActionReq:
			# self.__request = MessageRequest.SENSORS
			self.__request.append(MessageRequest.SENSORS)
			self.__performActionReq.notify()
			# self.__mainLogger.debug('SENSORS REQUEST : ' + str(self.__request))

	def readGroundSensorsRequest(self):
		with self.__performActionReq:
			# self.__request = MessageRequest.GROUND
			self.__request.append(MessageRequest.GROUND)
			self.__performActionReq.notify()
			# self.__mainLogger.debug('GROUND REQUEST : ' + str(self.__request))

	def readMotorsSpeedRequest(self) :
		with self.__performActionReq :
			# self.__request = MessageRequest.MOTORSREAD
			self.__request.append(MessageRequest.MOTORSREAD)
			self.__performActionReq.notify()

	def writeMotorsSpeedRequest(self, motorspeed):
		with self.__performActionReq:
			self.__motorspeed = motorspeed
			# self.__request = MessageRequest.MOTORS
			self.__request.append(MessageRequest.MOTORS)
			self.__performActionReq.notify()

	def writeColorRequest(self, color):
		with self.__performActionReq:
			self.__color = color
			# self.__request = MessageRequest.COLOR
			self.__request.append(MessageRequest.COLOR)
			self.__performActionReq.notify()

	def writeSoundRequest(self, sound):
		with self.__performActionReq:
			self.__sound = sound
			# self.__request = MessageRequest.SOUND
			self.__request.append(MessageRequest.SOUND)
			self.__performActionReq.notify()

	def killRequest(self) :
		with self.__performActionReq :
			self.__request.append(MessageRequest.KILL)
			# self.__request = MessageRequest.KILL
			self.__performActionReq.notify()

	def stopThymioRequest(self):
		with self.__performActionReq:
			self.__request.append(MessageRequest.STOP)
			# self.__request = MessageRequest.STOP
			self.__performActionReq.notify()


	def getMotorSpeed(self):
		return self.__motorspeed

	def getPSValues(self):
		return self.__psValue

	def getGroundSensorsValues(self):
		return (self.__psGroundAmbiantSensors, self.__psGroundReflectedSensors, self.__psGroundDeltaSensors)

	def __stopThymio(self) :
		# Red LEDs: Thymio stops moving
		self.__color = [32,16,0]
		self.__dbusSetColor()
		self.__motorspeed = [0,0]
		self.__dbusSetMotorspeed()

	def stop(self) :
		self.__stop.set()

	def killController(self) :
		self.__mainLogger.debug("ThymioController - Killing controller.")
		self.__stopThymio()
		self.__mainLogger.debug('Quit thymioController')
		self.__loop.quit()

	def run(self):
		self.__mainLogger.debug('ThymioController - Running.')

		# Run gobject loop
		self.__loop = gobject.MainLoop()
		self.__loop.run()
