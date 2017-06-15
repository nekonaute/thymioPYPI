import time
import glib, gobject
import dbus, dbus.mainloop.glib
import os
import threading
import traceback
import sys

"""
OCTOPY : ThymioController.py

Plays the role of interface between the simulation and the Thymio robot.
"""

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
AESL_PATH = os.path.join(CURRENT_FILE_PATH, ('asebaCommands.aesl'))

# Requests from the simulation
class MessageRequest() :
	NONE = -1

	# Read requests
	SENSORS, GROUND, STOP, MOTORSREAD, ACC, MIC = range(0, 6)

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
		self.__acc = [0,0,0]
		self.__motorspeed = [0,0]
		self.__color = [0,0,0]
		self.__sound = [0,0]
		self.__mic = [0]
		
		self.__newValue = {"PSValues":False, "GroundSensorsValues":False, "MotorSpeed":False, "AccValues":False, "MicValues":False}

		# Init the main loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		# Get stub of the Aseba network
		bus = dbus.SessionBus()
		# Create Aseba network 
		asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')
		self.__asebaNetwork = dbus.Interface(asebaNetworkObject, dbus_interface='ch.epfl.mobots.AsebaNetwork')
		# Load the aesl file
		self.__asebaNetwork.LoadScripts(AESL_PATH, reply_handler=self.__dbusEventReply, error_handler=self.__dbusError)
		self.__mainLogger.critical(self.__asebaNetwork.GetNodesList())
		# Schedules first run of the controller
		glib.idle_add(self.__execute)
	
	def __dbusError(self, e):
		# there was an error on D-Bus, stop loop
		self.__mainLogger.critical('Error in ThymioController: ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
		self.__mainLogger.critical('dbus error: %s' % str(e) + "\nNow sleeping for 1 second and retrying... ")
		time.sleep(1)
		#raise Exception("dbus error")

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
				self.__mainLogger.error("ThymioController - error getting variable : "+str(varName))
				ok = False
	
	def __dbusSetMotorspeed(self):
		self.__dbusSendEventName("SetSpeed", self.__motorspeed)

	def __dbusSetColor(self):
		self.__dbusSendEventName("SetColor", self.__color)

	def __dbusSetSound(self):
		self.__dbusSendEventName("SetSound", self.__sound)
	
	def __dbusGetProxSensorsReply(self, r):
		self.__psValue = r
		self.__newValue["PSValues"] = True

	def __dbusGetProxSensors(self):
		self.__dbusGetVariable("prox.horizontal", self.__dbusGetProxSensorsReply)

	def __dbusGetGroundAmbiantReply(self, r):
		self.__psGroundAmbiantSensors = r
		self.__newValue["GroundSensorsValues"] = True

	def __dbusGetGroundReflectedReply(self, r):
		self.__psGroundReflectedSensors = r
		self.__newValue["GroundSensorsValues"] = True

	def __dbusGetGroundDeltaReply(self, r):
		self.__psGroundDeltaSensors = r
		self.__newValue["GroundSensorsValues"] = True

	def __dbusGetGroundSensors(self):
		self.__dbusGetVariable("prox.ground.ambiant", self.__dbusGetGroundAmbiantReply)
		self.__dbusGetVariable("prox.ground.reflected", self.__dbusGetGroundReflectedReply)
		self.__dbusGetVariable("prox.ground.delta", self.__dbusGetGroundDeltaReply)

	def __dbusGetMotorSpeedLeftReply(self, r) :
		self.__motorspeed[0] = int(r)
		self.__newValue["MotorSpeed"] = True

	def __dbusGetMotorSpeedRightReply(self, r) :
		self.__motorspeed[1] = int(r)
		self.__newValue["MotorSpeed"] = True

	def __dbusGetMotorSpeed(self):
		self.__dbusGetVariable("motor.left.speed", self.__dbusGetMotorSpeedLeftReply)
		self.__dbusGetVariable("motor.right.speed", self.__dbusGetMotorSpeedRightReply)
		
	def __dbusGetAccReply(self,r):
		self.__acc = r
		self.__newValue["AccValues"] = True
	
	def __dbusGetAcc(self):
		self.__dbusGetVariable("acc", self.__dbusGetAccReply)
		
	def __dbusGetMicReply(self,r):
		self.__mic = r
		self.__newValue["MicValues"] = True
	
	def __dbusGetMic(self):
		self.__dbusGetVariable("mic.intensity", self.__dbusGetMicReply)

	def __execute(self):
		# Notifying that simulation has been set
		self.__simulation.thymioControllerPerformedAction()

		try :
			with self.__performActionReq:
				# Wait for requests:
				while len(self.__request) == 0 and not self.__stop.isSet() :
					self.__performActionReq.wait(0.1)

				while len(self.__request) :
					request = self.__request.pop(0)

					if request == MessageRequest.SENSORS :
						# Read sensor values
						self.__dbusGetProxSensors()
					elif request == MessageRequest.GROUND :
						# Read ground sensor values
						self.__dbusGetGroundSensors()
					elif request == MessageRequest.MOTORS :
						# Write motorspeed
						self.__dbusSetMotorspeed() # IF COMMENTED: wheels don't move
					elif request == MessageRequest.ACC:
						# Read accelerometer values
						self.__dbusGetAcc()
					elif request == MessageRequest.MIC:
						# Read accelerometer values
						self.__dbusGetMic()
					elif request == MessageRequest.MOTORSREAD :
						# Read motorspeed
						self.__dbusGetMotorSpeed()
					elif request == MessageRequest.COLOR :
						# Write Color
						self.__dbusSetColor()
					elif request == MessageRequest.SOUND :
						# Write Sound
						self.__dbusSetSound()
					elif request == MessageRequest.STOP :
						# Stop Thymio
						self.__stopThymio()

					# Notifying that simulation has been set
					self.__simulation.thymioControllerPerformedAction()
		except :
			self.__mainLogger.critical('ThymioController - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

		if self.__stop.isSet() :
			self.killController()
			return False
		else :
			return True

	def readSensorsRequest(self):
		with self.__performActionReq:
			self.__request.append(MessageRequest.SENSORS)
			self.__performActionReq.notify()

	def readGroundSensorsRequest(self):
		with self.__performActionReq:
			self.__request.append(MessageRequest.GROUND)
			self.__performActionReq.notify()

	def readMotorsSpeedRequest(self) :
		with self.__performActionReq :
			self.__request.append(MessageRequest.MOTORSREAD)
			self.__performActionReq.notify()
			
	def readAccRequest(self) :
		with self.__performActionReq :
			self.__request.append(MessageRequest.ACC)
			self.__performActionReq.notify()
			
	def readMicRequest(self) :
		with self.__performActionReq :
			self.__request.append(MessageRequest.MIC)
			self.__performActionReq.notify()

	def writeMotorsSpeedRequest(self, motorspeed):
		with self.__performActionReq:
			self.__motorspeed = motorspeed
			self.__request.append(MessageRequest.MOTORS)
			self.__performActionReq.notify()

	def writeColorRequest(self, color):
		with self.__performActionReq:
			self.__color = color
			self.__request.append(MessageRequest.COLOR)
			self.__performActionReq.notify()

	def writeSoundRequest(self, sound):
		with self.__performActionReq:
			self.__sound = sound
			self.__request.append(MessageRequest.SOUND)
			self.__performActionReq.notify()

	def killRequest(self) :
		with self.__performActionReq :
			self.__request.append(MessageRequest.KILL)
			self.__performActionReq.notify()

	def stopThymioRequest(self):
		with self.__performActionReq:
			self.__request.append(MessageRequest.STOP)
			self.__performActionReq.notify()

	def getMotorSpeed(self):
		self.__newValue["MotorSpeed"] = False
		return self.__motorspeed

	def getPSValues(self):
		self.__newValue["PSValues"] = False
		return self.__psValue

	def getGroundSensorsValues(self):
		self.__newValue["GroundSensorsValues"] = False
		return (self.__psGroundAmbiantSensors, self.__psGroundReflectedSensors, self.__psGroundDeltaSensors)

	def getAccValues(self):
		self.__newValue["AccValues"] = True
		return self.__acc
		
	def getMicValues(self):
		self.__newValue["MicValues"] = True
		return self.__mic
		
	def isNewValue(self, varName):
		"""
		Return True if the value of varName has been updated by the Thymio since the 
		last time the user got the value.
		
		:varName: String, "MotorSpeed", "PSValues", "GroundSensorsValues", "AccValues" or "MicValues"	
		:return: boolean
		"""
		if varName not in self.__newValue.keys():
			self.__mainLogger.error("ThymioController - isNewValue() : "+str(varName)+" is not a known value name")
		else:
			return self.__newValue[varName]

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
