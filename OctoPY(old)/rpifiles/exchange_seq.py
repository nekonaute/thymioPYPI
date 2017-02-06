import dbus, dbus.mainloop.glib
import glib, gobject
import threading, select
import argparse
import socket, struct, pickle
import json
import logging

import os, time, random, sys, traceback, datetime

import utils
from utils import recvall, recvOneMessage, sendOneMessage, MessageType

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(CURRENT_FILE_PATH, '..', 'config.json')
AESL_PATH = os.path.join(CURRENT_FILE_PATH, 'exchange_seq.aesl')
LOG_PATH = os.path.join(CURRENT_FILE_PATH, '..', 'log', 'exchange_seq.log')

MAX_SEQ_LENGTH = 6
SEQ_OPTIONS = ['F', 'B', 'L', 'R']
SEQ_OPTIONS_LENGTH = len(SEQ_OPTIONS)

MAX_EVAL = 10

# Reads the values contained in the passed configuration file and stores them in this object
class ConfigParser(object):
	def __init__(self, filename):
		json_data = open(filename)
		data = json.load(json_data)
		json_data.close()
		self.__address = data["simulation_address"]
		self.__port = data["simulation_port"]
		self.__neighbors = data["neighbors"]

	@property
	def address(self):
		return self.__address

	@property
	def port(self):
		return self.__port
	
	@property
	def neighbors(self):
		return self.__neighbors

# Represents a shared inbox object
class Inbox (object):
	def __init__(self):
		self.__inbox = list()
		self.__inboxLock = threading.Lock()

	def append(self, data):
		self.__inboxLock.acquire() #TODO: replace with "with"
		logging.debug('Acquired inbox lock')
		self.__inbox.append(data)
		logging.debug('Appended ' + str(data))
		self.__inboxLock.release()
		logging.debug('Released inbox lock')

	def popRandom(self):
		self.__inboxLock.acquire()
		item = None
		logging.debug('INBOX -' + str(self.__inbox))
		if self.__inbox:
			ran = random.randint(0, len(self.__inbox) - 1)
			item = self.__inbox.pop(ran)
		logging.debug('INBOX now -' + str(self.__inbox) + '- CHOSEN:' + str(item))
		self.__inboxLock.release()
		return item

# Listens to incoming connections from other agents and delivers them to the corresponding thread
class ConnectionsListener (threading.Thread):
	LOCALHOST = '127.0.0.1'

	def __init__(self, address, port, msgReceivers):
		threading.Thread.__init__(self)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((address, port))
		sock.listen(5)
		self.__address = address
		self.__port = port
		self.__socket = sock
		self.__msgReceivers = msgReceivers
		self.__isStopped = threading.Event()

	def run(self):
		try:
			logging.debug('ConnectionsListener - RUNNING')

			nStopSockets = 0
			iterator = self.__msgReceivers.itervalues()
			while nStopSockets < len(self.__msgReceivers):
				conn, (addr, port) = self.__socket.accept()
				if addr == self.LOCALHOST:
					iterator.next().setStopSocket(conn)
					nStopSockets += 1

			while not self.__stopped():
				logging.debug('ConnectionsListener - waiting for accept')
				conn, (addr, port) = self.__socket.accept()
				# stop socket has been set, we can deliver incoming connections to the receivers
				# if self.__stopped():
				# 	# the connection socket "conn" is the one from THIS client
				# 	logging.debug('ConnectionsListener - received request from ' + addr + ' - STOPPING __msgSenders')
				# 	for key in self.__msgSenders:
				# 		logging.debug('ConnectionsListener - Killing Receiver ' + key)
				# 		self.__msgSenders[key].stop(conn)
				# 		self.__msgSenders[key].join()
				# 	conn.close()
				# 	break
				# else:
					# the connection socket is from a remote host
				if not self.__stopped():
					try:
						logging.debug('ConnectionsListener - received request from ' + addr + ' - FORWARDING to Receiver')
						self.__msgReceivers[addr].setConnectionSocket(conn)
					except:
						# Received connection from unknown IP
						logging.warning("Exception: " + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

			logging.debug('ConnectionsListener STOPPED -> EXITING...')
		except:
			logging.critical('Error in ConnectionsListener: ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

	def stop(self):
		self.__isStopped.set()
		logging.debug('CL - set stopped')
		# If blocked on accept() wakes it up with a fake connection
		fake = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		logging.debug('CL - fake connection')
		fake.connect(('localhost', 44444))
		logging.debug('CL - fake connection done')
		fake.close()

	def __stopped(self):
		return self.__isStopped.isSet()	

# Waits for incoming messages on one socket and stores them in the shared inbox
class MessageReceiver (threading.Thread):
	def __init__(self, ipAddress, inbox):
		threading.Thread.__init__(self)
		self.__ipAddress = ipAddress
		self.__inbox = inbox
		self.__connectionSocket = None
		self.__isSocketAlive = threading.Condition()
		self.__isStopped = threading.Event()
		self.__stopSocket = None
		self.__isStopSocketAlive = threading.Event()

	@property
	def ipAddress(self):
		return self.__ipAddress

	def setConnectionSocket(self, newSock):
		self.__isSocketAlive.acquire()
		if not self.__connectionSocket and newSock:
			self.__connectionSocket = newSock
			logging.debug('Receiver - ' + self.__ipAddress + ' - CONNECTED!!!')
			self.__isSocketAlive.notify()
		self.__isSocketAlive.release()

	def setStopSocket(self, stopSock):
		self.__stopSocket = stopSock

	def __recvOneMessage(self, socket):
		logging.debug('Receiver - ' + self.__ipAddress + ' - receiving...')
		lengthbuf = recvall(socket, 4)
		length, = struct.unpack('!I', lengthbuf)
		data = pickle.loads(recvall(socket, length))
		logging.debug('Receiver - ' + self.__ipAddress + ' - got it' + str(data))
		return data

	def run(self):
		try:
			logging.debug('Receiver - ' + self.__ipAddress + ' - RUNNING')
			# # Waits while the stop socket is not set
			# while not self.__isStopSocketAlive.isSet():
			# 	self.__isStopSocketAlive.wait()

			while not self.__stopped():
				
				# Waits while the connection is not set
				self.__isSocketAlive.acquire()
				if not self.__connectionSocket and not self.__stopped():
					logging.debug('Receiver - ' + self.__ipAddress + ' - NOT CONNECTED: WAIT')
					self.__isSocketAlive.wait()
				self.__isSocketAlive.release()

				if not self.__stopped():
					logging.debug('Receiver - ' + self.__ipAddress + ' - waiting on select')
					readable, _, _ = select.select([self.__connectionSocket, self.__stopSocket], [], [])
					if self.__stopSocket in readable:
						# 	Received a message (stop) from localhost
						logging.debug('Receiver - ' + self.__ipAddress + ' - StopSocket is in readable')
						data = self.__recvOneMessage(self.__stopSocket)
						logging.debug('Received ' + data)
					elif self.__connectionSocket in readable:
						logging.debug('Receiver - ' + self.__ipAddress + ' - ConnectionSocket is in readable')
						# 	Received a message from remote host
						try:
							data = self.__recvOneMessage(self.__connectionSocket)
							logging.debug('Receiver - ' + self.__ipAddress + ' - Received ' + str(data))
							if data and not self.__stopped():
								logging.debug('Receiver - ' + self.__ipAddress + ' - Appending ' + str(data))
								self.__inbox.append(data)
								logging.debug('Receiver - ' + self.__ipAddress + ' appended ' + str(data) + ' to inbox.')
							else:
								logging.debug('Receiver - ' + self.__ipAddress + ' - time to die.')
						except: #TODO: wrong position?
							# Error while receiving: current socket is corrupted -> closing it
							logging.warning('Receiver - ' + self.__ipAddress + ' - Error while receiving - CLOSING socket!')
							self.__connectionSocket.close()
							self.__connectionSocket = None
		except:
			logging.critical('Error in Receiver ' + self.__ipAddress + ': ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

		logging.debug('Receiver - ' + self.__ipAddress + ' - STOPPED -> EXITING...')

	def stop(self):
		self.__isStopped.set()
		logging.debug('Receiver - ' + self.__ipAddress + ' set stopped')
		self.__isSocketAlive.acquire()
		logging.debug('Receiver - ' + self.__ipAddress + ' acquired __isSocketAlive')
		self.__isSocketAlive.notify()
		logging.debug('Receiver - ' + self.__ipAddress + ' notified __isSocketAlive')
		self.__isSocketAlive.release()		
		logging.debug('Receiver - ' + self.__ipAddress + ' released __isSocketAlive')
		# # If receiver is blocked on select, wake it up with a STOP message on stopSocket
		# # TODO: replace with just a close() call?
		# try:
		# 	packed_data = pickle.dumps('STOP')
		# 	length = len(packed_data)
		# 	self.__stopSocket.sendall(struct.pack('!I', length))
		# 	self.__stopSocket.sendall(packed_data)
		# 	logging.debug('Receiver - ' + self.__ipAddress + ' sent stop message')
		# except:
		# 	logging.debug('Receiver - ' + self.__ipAddress + ' connection interrupted before stop message')

	def __stopped(self):
		return self.__isStopped.isSet()

# Sends outgoing messages to the remote host
class MessageSender (threading.Thread):
	def __init__(self, ipAddress, port):
		threading.Thread.__init__(self)
		self.__ipAddress = ipAddress
		self.__port = port
		self.__outbox = list()
		self.__outboxReady = threading.Condition()
		self.__connectionSocket = None
		self.__isStopped = threading.Event()

	@property
	def ipAddress(self):
		return self.__ipAddress

	def __estabilishConnection(self):
		nAttempt = 0
		if self.__connectionSocket:
			logging.debug('Sender - ' + self.__ipAddress + ' - ALREADY CONNECTED')
			return True
		# Otherwise retry to connect unless stop signal is sent
		while not self.__stopped():
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((self.__ipAddress, self.__port))
				self.__connectionSocket = sock
				logging.debug('Sender - ' + self.__ipAddress + ' - CONNECTED @ attempt' + str(nAttempt))
				return True
			except:
				# Error during connect, new attempt if not stopped
				nAttempt += 1
		return False

	def outboxAppend(self, item):
		self.__outboxReady.acquire()
		self.__outbox.append(item)
		logging.debug('Controller - APPENDED ' + str(item) + ' to ' + self.__ipAddress + ' OUTBOX: ' + str(self.__outbox))
		self.__outboxReady.notify()
		self.__outboxReady.release()

	def __outboxPop(self):
		item = None
		self.__outboxReady.acquire()
		if not self.__outbox:
			logging.debug('Sender - ' + self.__ipAddress + ' - EMPTY OUTBOX: WAIT')
			self.__outboxReady.wait()
		if not self.__stopped():
			logging.debug('Sender - ' + self.__ipAddress + ' - OUTBOX is' + str(self.__outbox) + ' - taking ' + str(self.__outbox[0]))
			item = self.__outbox.pop(0)
		self.__outboxReady.release()
		return item
		
	def __sendOneMessage(self, data):
		packed_data = pickle.dumps(data)
		length = len(packed_data)
		self.__connectionSocket.sendall(struct.pack('!I', length))
		self.__connectionSocket.sendall(packed_data)

	def run(self):
		try:
			logging.debug('Sender - ' + self.__ipAddress + ' - RUNNING')
			while not self.__stopped():
				item = self.__outboxPop()
				logging.debug('Sender - ' + self.__ipAddress + ' - OUTBOX popped ' + str(item))
				if item and self.__estabilishConnection():
					# Not stopped and has an item to send and an estabilished connection
					try:
						self.__sendOneMessage(item)
						logging.debug('Sender - ' + self.__ipAddress + ' - SENT' + str(item))
					except:
						# Error while sending: put back item in the outbox
						self.__outboxReady.acquire()
						self.__outbox.insert(0, item)
						self.__outboxReady.release()
						# Current socket is corrupted: closing it
						self.__connectionSocket.close()
						self.__connectionSocket = None
						logging.warning('Sender - ' + self.__ipAddress + ' - Error while sending - CLOSED socket and restored OUTBOX:' + str(self.__outbox))
			logging.debug('Sender - ' + self.__ipAddress + ' - STOPPED -> EXITING...')
		except:
			logging.critical('Error in Sender ' + self.__ipAddress + ': ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

	def stop(self):
		self.__isStopped.set()
		self.__outboxReady.acquire()
		self.__outboxReady.notify()
		self.__outboxReady.release()

	def __stopped(self):
		return self.__isStopped.isSet()				

# Reads messages from the shared inbox and moves the Thymio accordingly, 
# then generates a message and delivers it to the MessageSenders
class ThymioController(object):

	def __init__(self, inbox, msgSenders):
		# Init parameters
		self.__inbox = inbox
		self.__msgSenders = msgSenders
		self.__nEval = 0

		# This seems to be somehow necessary when no X server is running		
		# os.environ['DBUS_SESSION_BUS_ADDRESS'] = "unix:path=/run/dbus/system_bus_socket"
		# os.environ["DISPLAY"] = ":0"

		# Init the main loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		
		# Get stub of the Aseba network
		# if systemBus:
		# 	bus = dbus.SystemBus()
		# else:
		bus = dbus.SessionBus()

		# Create Aseba network 
		asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')
		self.__asebaNetwork = dbus.Interface(asebaNetworkObject, dbus_interface='ch.epfl.mobots.AsebaNetwork')
		logging.debug('Aseba nodes: ' + str(self.__asebaNetwork.GetNodesList()))
		
		# Load the aesl file
		self.__asebaNetwork.LoadScripts(AESL_PATH, reply_handler=self.__dbusEventReply, error_handler=self.__dbusError)

		# Schedules first run of the controller
		glib.idle_add(self.__execute)

	def __dbusEventReply(self):
		# correct replay on D-Bus, ignore
		pass

	def __dbusError(self, e):
		# there was an error on D-Bus, stop loop
		logging.critical('dbus error: %s' % str(e))
		self.__loop.quit()

	def __dbusSendEventName(self, eventName, params):
		self.__asebaNetwork.SendEventName(eventName, params, 
			reply_handler=self.__dbusEventReply, error_handler=self.__dbusError)

	def __move(self, speeds, sleepTime):
		self.__dbusSendEventName("SetSpeed", speeds)
		time.sleep(sleepTime) # TODO: better movement: not time.sleep but in AESL file
		self.__dbusSendEventName("SetSpeed", [0,0])

	def __goForward(self):
		self.__move([150,150], 2)

	def __goBackward(self):
		self.__move([-150,-150], 2)

	def __turnLeft(self):
		self.__move([-150,150], 1.6)

	def __turnRight(self):
		self.__move([150,-150], 1.6)

	def __randomSeqGenerator(self):
		randomSeq = list()
		randomLength = random.randint(1, MAX_SEQ_LENGTH)
		for i in range(0, randomLength):
			randIndex = random.randint(0, SEQ_OPTIONS_LENGTH - 1)
			randomSeq.append(SEQ_OPTIONS[randIndex])
		return randomSeq

	def __execute(self):
		logging.debug('Controller - EXECUTING')
		# if no loop is running, skip function
		if not self.__loop.is_running():
			return False

		# if maximum number of evaluation reached, stop script
		if self.__nEval == MAX_EVAL:
			self.stop()
			return False
		
		logging.debug('Controller - evaluation ##### ' + str(self.__nEval) + ' #####')
		
		seqToExecute = self.__inbox.popRandom()
		if not seqToExecute:
			seqToExecute = self.__randomSeqGenerator()
			logging.debug('Controller - no incoming seq -> GENERATING ' + str(seqToExecute))
			# Cyano LEDs: execute the generated sequence
			self.__dbusSendEventName("SetColor", [0,32,32])
		else:
			# Green LEDs: execute the received sequence
			self.__dbusSendEventName("SetColor", [0,32,0])	

		logging.debug('Controller - MOVING ' + str(seqToExecute))
		while seqToExecute:
			action = seqToExecute.pop(0)
			if action == 'F':
				self.__goForward()
			elif action == 'B':
				self.__goBackward()
			elif action == 'L':
				self.__turnLeft()
			elif action == 'R':
				self.__turnRight()
		# time.sleep(1) # execution time
		
		# Blue LEDs: rest for 2 seconds
		logging.debug('Controller - Blue: RESTING')
		self.__dbusSendEventName("SetColor", [0,0,32])
		time.sleep(2)

		# Yellow LEDs: generate and send a random sequence
		logging.debug('Controller - Yellow: generating sequence')
		self.__dbusSendEventName("SetColor", [32,32,0])
		seqToSend = self.__randomSeqGenerator()
		time.sleep(2) # calculation time
		for key in self.__msgSenders:
			self.__msgSenders[key].outboxAppend(seqToSend)

		self.__nEval += 1

		if not self.__loop.is_running():
			self.__dbusSendEventName("SetColor", [32,0,0])
			self.__dbusSendEventName("SetSpeed", [0,0])
			return False

		return True

	def run(self):
		# Run gobject loop
		logging.debug('Controller - RUNNING')
		self.__loop = gobject.MainLoop()
		self.__loop.run()

	def stop(self):
		# Red LEDs: Thymio stops working
		self.__loop.quit()
		self.__dbusSendEventName("SetColor", [32,0,0])
		self.__dbusSendEventName("SetSpeed", [0,0])

# Represents an entire simulation: starts the proper thread 
class Simulation(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		# To avoid conflicts between gobject and python threads
		gobject.threads_init()
		dbus.mainloop.glib.threads_init()

		self.__stopped = False

		# JSON configuration file parser
		config = ConfigParser(CONFIG_PATH)

		# Initialize message receivers
		inbox = Inbox()
		self.__msgReceivers = dict()
		for neigh in config.neighbors:
			address = neigh["address"]
			self.__msgReceivers[address] = MessageReceiver(address, inbox)

		# Incoming connections listener
		self.__connListener = ConnectionsListener(config.address, config.port, self.__msgReceivers)
		self.__stopSockets = list()

		# Initialize and start message senders
		self.__msgSenders = dict()
		for neigh in config.neighbors:
			address = neigh["address"]
			self.__msgSenders[address] = MessageSender(address, neigh["port"])

		# Thymio controller
		self.__thymioC = ThymioController(inbox, self.__msgSenders)

	def run(self):
		try:
			self.__connListener.start()
			logging.debug('ConnectionsListener started')

			# Set connections for stopping the receivers
			for i in range (0, len(self.__msgReceivers)):
				stopSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				stopSocket.connect(('localhost', 44444))
				self.__stopSockets.append(stopSocket)
			
			# Starts message receivers
			for addr in self.__msgReceivers:
				self.__msgReceivers[addr].start()

			# Starts message senders
			for addr in self.__msgSenders:
				self.__msgSenders[addr].start()

			self.__thymioC.run() 
			# Main loop is now in thymio controller, run() will resume when thymioC stops
			logging.debug('Controller: KILLED')

			self.stop()
			logging.debug('Exiting run()...' + '\n')
		except:
			logging.critical('Error in Simulation: ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

	def stop(self):
		if self.__stopped:
			logging.debug('Simulation already stopped')
			return
		self.__stopped = True
		# Stopping Thymio Controller
		self.__thymioC.stop()

		# Stopping all the message senders: no more outgoing messages
		for addr in self.__msgSenders:
			logging.debug('Killing Sender ' + addr)
			self.__msgSenders[addr].stop()
			self.__msgSenders[addr].join()
		logging.debug('All MessageSenders: KILLED')

		# Stopping connections listener: no more incoming connections
		self.__connListener.stop()
		self.__connListener.join()
		logging.debug('ConnectionsListener: KILLED')

		# Stopping all the message receivers: no more incoming messages
		i = 0
		for addr in self.__msgReceivers:
			logging.debug('Killing Receiver ' + addr)
			self.__msgReceivers[addr].stop()
			# Send stop messages
			packed_data = pickle.dumps('STOP')
			length = len(packed_data)
			self.__stopSockets[i].sendall(struct.pack('!I', length))
			self.__stopSockets[i].sendall(packed_data)
			self.__msgReceivers[addr].join()
			self.__stopSockets[i].close()
			i += 1
		logging.debug('All MessageReceivers: KILLED')

SERVER_HOST = ''
SERVER_PORT = 55555
TRUSTED_CLIENTS = ['127.0.0.1', '192.168.1.100', '192.168.0.110', '192.168.0.210']

if __name__ == '__main__':
	# Checking for debug:
	parser = argparse.ArgumentParser(description='Runs the exchange sequence program.')
	parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, 
		help='run the simulation printing debug information')
	parser.add_argument('-i', '--hostIP', type = str, default = None, help = 'IP of the host which initialized this thymio')
	options = parser.parse_args()
	
	# lev = logging.INFO
	# if options.debug:
	# 	lev = logging.DEBUG
	logging.basicConfig(filename=LOG_PATH, format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

	logging.debug("OK LOGGING")

	# Create socket to send ACK to the host if need be
	# if options.hostIP != None:
	# 	try:
	# 		logging.debug('Sending ACK to ' + options.hostIP)
	# 		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 		sock.connect((options.hostIP, SERVER_PORT))
	# 		optSend = DirtyMessage()
	# 		optSend.message = 99
	# 		sendOneMessage(sock, optSend) 
	# 	except:
	# 		logging.critical('Error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
	# 	logging.debug('Done !')

	# global TRUSTED_CLIENTS
	# if options.hostIP != None :
	# 	TRUSTED_CLIENTS.append(options.hostIP)

	logging.debug("INITIATING SOCKET")

	# Create socket for listening to simulation commands
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((SERVER_HOST, SERVER_PORT))
	sock.listen(5)
	simulation = None

	logging.debug("OK SOCKET")
	
	cpt = 0
	while 1:
		try:
			# waiting for client...
			conn, (addr, port) = sock.accept()
			logging.debug('Received command from (' + addr + ', ' + str(port) + ')')
			if addr not in TRUSTED_CLIENTS:
				logging.error('Received connection request from untrusted client (' + addr + ', ' + str(port) + ')')
				continue
			
			# receive one message
			logging.debug('Receiving...')
			lengthbuf = recvall(conn, 4)
			length, = struct.unpack('!I', lengthbuf)
			recvOptions = pickle.loads(recvall(conn, length))
			logging.debug('Received ' + str(recvOptions))

			if recvOptions.msgType == MessageType.KILL:
				logging.critical("KILL")
				if simulation:
					simulation.stop()
				break

			if recvOptions.msgType == MessageType.START and not simulation: # TODO: or simulation.isFinished()
				# start the simulation
				simulation = Simulation()
				simulation.start()
				print("OUI ?")
			elif not recvOptions.msgType == MessageType.STOP and simulation:
				logging.critical("STOP")
				# stop the simulation
				simulation.stop()
				simulation = None
		except:
			logging.critical('Error in main: ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
			exit(1)
