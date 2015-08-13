import OctoPY
import Params

import threading

from abc import ABCMeta, abstractmethod

class Controller(threading.Thread) :
	__metaclass__ = ABCMeta
	staticID = 0

	# Compulsory parameters
	compParams = ['controller_name', 'controller_path']

	def __init__(self, detached) :
		threading.Thread.__init__(self)

		if detached :
			self.daemon = True

		self.__stop == threading.Event()
		self.__ID = Controller.getID()

		self.__msgListener = None


	@staticmethod
	def getID() :
		Controller.staticID += 1
		return Controller.staticID - 1

	def getID(self) :
		return self.__ID

	ID = property(getID)

		
	def run(self) :
		self.preActions()

		while not self.__stop.isSet() :
			self.step()

		self.postActions()

		# We stop the listener if needs be
		if self.__msgListener != None :
			self.__msgListener.stop()
			self.__msgListener = None

	@abstractmethod
	def step(self) :
		pass

	def preActions(self) :
		pass

	def postActions(self) :
		pass		


	def stop(self) :
		self.__stop.set()

	def log(self, message, level = logging.DEBUG) :
		OctoPY.logger.log(level, message)


	def register(self, IPs = []) :
		# We create the message listener for the notifications if needs be
		if self.__msgListener == None :
			self.__msgListener = MessageListener(self)
			self.__msgListener.start()

		OctoPY.registerController(self, IPs)


	def notify(self, **params) :
		pass


	@staticmethod
	def checkForCompParams() :
		for param in Controller.compParams :
			if not Params.params.checkParam(param) :
				OctoPY.logger.error("Controller - Parameter " + param + " not found.", )
				return False

		return True



class MessageListener(threading.Thread) :
	def __init__(self, controller, logger) :
		threading.Thread.__init__(self)

		self.__controller = controller

		# We set daemon to True so that MessageListener exits when the main thread is killed
		self.daemon = True

		self._stop = threading.Event()

		# Create socket for listening to simulation commands
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__sock.bind((COMMANDS_LISTENER_HOST, COMMANDS_LISTENER_PORT))
		self.__sock.listen(5)

	def run(self):
		while not self.__stop.isSet() :
			try:
				# Waiting for client...
				OctoPY.logger.debug("MessageListener - Waiting on accept...")
				conn, (addr, port) = self.__sock.accept()

				# OctoPY.logger.debug('MessageListener - Received command from (' + addr + ', ' + str(port) + ')')
				# if addr not in TRUSTED_CLIENTS:
				# 	OctoPY.logger.error('MessageListener - Received connection request from untrusted client (' + addr + ', ' + str(port) + ')')
				# 	continue
				
				# Receive one message
				OctoPY.logger.debug('MessageListener - Receiving message...')
				message = recvOneMessage(conn)
				OctoPY.logger.debug('MessageListener - Received ' + str(message))

				# The listener transmits the desired message
				if message.msgType == MessageType.NOTIFY :
					message.data["hostIP"] = addr
					self.__controller.notify(**message.data)
					messageCommand = MessageCommand.START
			except:
				OctoPY.logger.critical('MessageListener - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

		OctoPY.logger.debug('MessageListener - Exiting...')

	def stop(self) :
		self.__stop.set()