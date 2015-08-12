#!/usr/bin/env python

import argparse
import subprocess
import sys
import os
import re
import logging
import traceback
import json
import socket, select
import struct
import pickle

import importlib
import ipaddress
import paramiko
import cmd

import utils
import Params
import Controller
from utils import recvall, recvOneMessage, sendOneMessage, MessageType

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

HOSTNAMES_TABLE_FILE_PATH = os.path.join(CURRENT_FILE_PATH, 'hostnames_table.json')

LOG_PATH = os.path.join(CURRENT_FILE_PATH, 'log', 'OctoPY.log')

THYMIO_SCRIPTS_PATH = '/home/pi/dev/thymioPYPI/OctoPY/rpifiles'

PIUSERNAME = 'pi'
PIPASSWORD = 'pi'

LISTENER_HOST = ''
LISTENER_PORT = 55555

TIMEOUT_ACK = 10
TIMEOUT_QUERY = 5

octoPYInstance = None

class OctoPY() :
	def __init__(self, log, debug) :
		self.__hashThymiosHostnames = None
		self.__listThymiosStates = None
		self.__controllers = []

		# Creation of the logging handlers
		level = logging.INFO
		if debug :
			level = logging.DEBUG

		self.__logger = logging.getLogger()
		self.__logger.setLevel(level)

		# File Handler
		if args.log :
			fileHandler = logging.FileHandler(LOG_PATH)
			formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
			fileHandler.setFormatter(formatter)
			fileHandler.setLevel(level)
			self.__logger.addHandler(fileHandler)

		# Console Handler
		consoleHandler = logging.StreamHandler()
		consoleHandler.setLevel(level)
		self.__logger.addHandler(consoleHandler)

		# We load the hostnames table (if it exists)
		if os.path.isfile(HOSTNAMES_TABLE_FILE_PATH) :
			self.loadHostnamesTable()
		else :
			self.__logger.debug("No existing hostnames table found")


	def getLogger(self) :
		return self.__logger

	logger = property(getLogger)


	def getHashThymiosHostnames(self) :
		return self.__hashThymiosHostnames

	hashThymiosHostnames = property(getHashThymiosHostnames)


	def getListThymiosStates(self) :
		return self.__listThymiosStates

	listThymiosStates = property(getListThymiosStates)


	def saveHostnamesTable(self) :
		self.__logger.info("saveHostnamesTable - Saving hostnames table")

		if self.__hashThymiosHostnames != None :
			try :
				with open(HOSTNAMES_TABLE_FILE_PATH, 'w') as fileOutput :
					json.dump(self.__hashThymiosHostnames, fileOutput)
			except :
				self.__logger.critical("Unexpected error in saveHostnamesTable : " + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc()) 
		else :
			self.__logger.error("No table created")

	def loadHostnamesTable(self) :
		self.__logger.info("loadHostnamesTable - Loading hostnames table")

		try :
			with open(HOSTNAMES_TABLE_FILE_PATH, 'r') as fileInput :
				self.__hashThymiosHostnames = json.load(fileInput)

			self.__logger.debug("loadHostnamesTable - hostnames table :")
			for hostname in self.__hashThymiosHostnames :
				self.__logger.debug("\t " + hostname + " : " + str(self.__hashThymiosHostnames[hostname]))
		except :
			self.__logger.critical("Unexpected error in loadHostnamesTable : " + str(sys.exc_info()[0]) + ' - ' +traceback.format_exc())


	def lookUp(self, rangeArg) :
		try :
			self.__logger.info("lookUp - excuting nmap")

			# Popen calls the nmap command in the range specified by rangeArg
			proc = subprocess.Popen(["nmap", "-sn", rangeArg], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

			(out, err) = proc.communicate()

			if proc.returncode < 0 :
				self.__logger.error("lookUp - Error executing nmap : " + str(err))
				exit(1)

			# We look for all up hosts
			tabIP = []

			lines = out.splitlines()
			regHost = re.compile(r"^Host is up")
			regIP = re.compile(r"^Nmap scan report for (\d+\.\d+\.\d+\.\d+)$")
			cpt = 0
			while cpt < len(lines) :
				if regHost.search(lines[cpt]) :
					if cpt > 0 :
						s = regIP.search(lines[cpt - 1])
						if s :
							tabIP.append(str(ipaddress.ip_address(u'' + s.group(1))))
							# tabIP.append(ipaddress.ip_address(u'' + s.group(1)))

				cpt += 1

			self.__logger.info("lookUp - nmap done")

			if len(tabIP) == 0 :
				self.__logger.info("lookUp - no up thymios were found !")
				return

			self.__logger.debug("lookUp - IP address for up thymios found :")
			for IP in tabIP :
				self.__logger.debug("\t " + str(IP))

			self.__logger.info("lookUp - Gathering thymios' hostnames")

			self.__hashThymiosHostnames = {}

			# We query each thymio for its hostname
			for IP in tabIP :
				self.__logger.info("lookUp - ssh on " + str(IP))

				ssh = paramiko.SSHClient()
				ssh.load_system_host_keys()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

				# We don't want to be bothered with paramiko logging unless it's critical
				paramikoLogger = logging.getLogger('paramiko')
				paramikoLogger.setLevel('CRITICAL')

				# Connection on the raspberry
				ssh.connect(str(IP), username = PIUSERNAME, password = PIPASSWORD)

				# Executing command hostname
				stdin, stdout, stderr = ssh.exec_command('hostname')

				hostname = str(stdout.read()).rstrip('\n')
				ssh.close()

				self.__logger.info("lookUp - active thymio: " + hostname + " - " + str(IP))

				if hostname in self.__hashThymiosHostnames.keys() :
					self.__logger.warning("lookUp - warning: multiple thymios with hostname " + hostname + " : " + str(self.__hashThymiosHostnames[hostname]) + " and " + str(IP))

				self.__hashThymiosHostnames[hostname] = IP

			self.__logger.debug("lookUp - hostname/IP table :")
			for hostname in self.__hashThymiosHostnames :
				self.__logger.debug("\t " + hostname + " : " + str(self.__hashThymiosHostnames[hostname]))

			self.saveHostnamesTable()

		except :	
			self.__logger.critical("Unexpected error in lookUp : " + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc()) 


	def getHostnameFromIP(self, IP) :
		if self.__hashThymiosHostnames :
			for hostname in self.__hashThymiosHostnames.keys() :
				if self.__hashThymiosHostnames[hostname] == IP :
					return hostname

		return None

	def resolveAddresses(self, IPs) :
		# List of recipients
		dest = []
		if len(IPs) > 0 :
			recipList = IPs

			self.__logger.debug("resolveAddresses - recipients list : " + ' '.join(recipList))

			# Resolution of hostnames to IP address
			for recip in recipList :
				if self.__hashThymiosHostnames != None and recip in self.__hashThymiosHostnames.keys() :
					dest.append(self.__hashThymiosHostnames[recip])
				else :
					# We verify that this is a correct IP address
					try :
						dest.append(ipaddress.ip_address(u'' + recip))
					except :
						self.__logger.debug("resolveAddresses - " + recip + " is not a known host nor a valid IP address")
						continue
		else :
			# If no host was specified, we send to every known hosts
			if self.__hashThymiosHostnames != None :
				dest = [ipaddress.ip_address(u'' + IP) for IP in self.__hashThymiosHostnames.values()]
			else :
				self.__logger.critical("resolveAddresses - No hosts specified and no existing hostnames table")
				return None

		return dest


	def sendMessage(self, message, IPs, data = None) :
		# Message
		message = int(message)

		# Addresses resolution
		dest = self.resolveAddresses(IPs)

		myIP = None
		if dest != None :
			# sockACK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# sockACK.setblocking(0)
			# sockACK.bind((ACKLISTENER_HOST, ACKLISTENER_PORT))
			# sockACK.listen(5)

			for destIP in dest :
				self.__logger.info("sendMessage - sending message " + str(message) + " to " + str(destIP))

				optSend = utils.Message()

				try :
					# Init thymio
					if message == MessageType.INIT :
						# ssh = paramiko.SSHClient()
						# ssh.load_system_host_keys()
						# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

						# # We don't want to be bothered with paramiko self.__logger unless it's critical
						# paramikoLogger = self.__logger.getLogger('paramiko')
						# paramikoLogger.setLevel('CRITICAL')

						# # Connection on the raspberry
						# ssh.connect(str(destIP), username = PIUSERNAME, password = PIPASSWORD)
						# transport = ssh.get_transport()
						# session = transport.open_session()
						# session.request_x11(single_connection=True)

						# # We get our IP address on this network
						# if myIP == None :
						# 	stdin, stdout, stderr = ssh.exec_command('echo $SSH_CLIENT')
						# 	myIP = ipaddress.ip_address(u'' + stdout.read().split(' ')[0])

						# # Executing command hostname
						# # stdin, stdout, stderr = ssh.exec_command('sh ' + os.path.join(THYMIO_SCRIPTS_PATH, '_init_thymio.sh') + ' ' + str(myIP))
						# session.exec_command('sh ' + os.path.join(THYMIO_SCRIPTS_PATH, '_init_thymio.sh') + ' ' + str(myIP))

						# session.close()
						# ssh.close()

						sshcommand = ["/usr/bin/sshpass", "-p", PIPASSWORD, "ssh", "-X", PIUSERNAME + "@" + str(destIP)]
						if myIP == None :
							proc = subprocess.Popen(["hostname", "-I"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
							(out, err) = proc.communicate()

							myIP = ipaddress.ip_address(u'' + out.split(' ')[0])

						# proc = subprocess.Popen(sshcommand + ["asebamedulla", "ser:device=/dev/ttyACM0", "&", "python", "/home/pi/pithymio.py"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
						proc = subprocess.Popen(sshcommand + ["asebamedulla", "ser:device=/dev/ttyACM0", "&", "python", os.path.join(THYMIO_SCRIPTS_PATH, 'MainController.py'), '-d', '-i', str(myIP), '&'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
						# proc = subprocess.Popen(sshcommand + ["sh", os.path.join(THYMIO_SCRIPTS_PATH, '_init_thymio.sh'), str(myIP)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
						# proc.wait()

					# Start simulation
					elif message == MessageType.START :
						optSend.msgType = MessageType.START
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)

					# Pause simulation
					elif message == MessageType.PAUSE :
						optSend.msgType = MessageType.PAUSE
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)

					# Restart simulation
					elif message == MessageType.RESTART :
						optSend.msgType = MessageType.RESTART
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)

					# Set simulation
					elif message == MessageType.SET :
						optSend.msgType = MessageType.SET
						optSend.data = data
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)				

					# Stop simulation
					elif message == MessageType.STOP :
						optSend.msgType = MessageType.STOP
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)

					# Kill thymio
					elif message == MessageType.KILL :
						optSend.msgType = MessageType.KILL
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)

					# Register as observer
					elif message == MessageType.REGISTER :
						optSend.msgType = MessageType.REGISTER
						optSend.data = data
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.connect((str(destIP), 55555))
						sendOneMessage(sock, optSend)

					else :
						self.__logger.critical("sendMessage - not a known message id : " + str(message))
						return
				except :
					self.__logger.error("sendMessage - Unexpected error while sending message " + str(message) + " to " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
					continue


	def queryThymios(self, IPs) :
		dest = resolveAddresses(IPs)

		if dest != None :
			try :
				newDest = dest
				downHosts = []
				for destIP in dest :
					# We first ping each recipient
					self.__logger.info("queryThymios - pinging " + str(destIP))
					proc = subprocess.Popen(['ping', str(destIP), '-c1', '-W2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
					(stdout, stderr) = proc.communicate()
					
					if proc.returncode != 0 :
						self.__logger.info("queryThymios - " + str(destIP) + " is not up")
						downHosts.append(destIP)
						newDest.remove(destIP)
					else :
						self.__logger.info("queryThymios - " + str(destIP) + " is up")

				dest = newDest
			except :
				self.__logger.critical("queryThymios - Unexpected error while pinging " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc())
				exit(1)


			waitingAnswer = []
			sockAnswer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockAnswer.setblocking(0)
			sockAnswer.bind((LISTENER_HOST, LISTENER_PORT))
			sockAnswer.listen(5)

			optSend = Message()
			optSend.message = MessageType.QUERY
			for destIP in dest :
				try :
					# We send a message to each recipient
					self.__logger.info("queryThymios - sending query to " + str(destIP))
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((str(destIP), 55555))
					sendOneMessage(sock, optSend)
					waitingAnswer.append(str(destIP))
				except :
					self.__logger.error("queryThymios - Unexpected error while sending query to " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
					continue


			# Waiting for answers
			timeOut = TIMEOUT_QUERY
			listeningHosts = []
			startedHosts = []
			sleepingHosts = []
			while len(waitingAnswer) > 0 :
				self.__logger.debug('queryThymios - Waiting answer from ' + ' '.join(waitingAnswer))
				readable, writable, exceptional = select.select([sockAnswer], [], [], timeOut)

				# If a timeout happend
				if not (readable or writable or exceptional) :
					self.__logger.debug('queryThymios - No answer from ' + ' '.join(waitingAnswer) + ' after ' + str(timeOut) + ' seconds')
					sleepingHosts = waitingAnswer
					break
				else :
					for sock in readable :
						conn, (addr, port) = sock.accept()
						self.__logger.debug('queryThymios - Receiving message from ' + str(addr))

						data = recvOneMessage(conn)
						if data.message == MessageType.LISTENING :
							self.__logger.debug('queryThymios - LISTENING received from ' + str(addr))
							waitingAnswer.remove(addr)
							listeningHosts.append(addr)
						elif data.message == MessageType.STARTED :
							self.__logger.debug('queryThymios - STARTED received from ' + str(addr))
							waitingAnswer.remove(addr)
							startedHosts.append(addr)
						else :
							self.__logger.error("queryThymios - not an expected message " + str(message) + " from " + str(addr))
							waitingAnswer.remove(addr)
							continue

			self.__listThymiosStates = []
			for IP in downHosts :
				hostname = getHostnameFromIP(IP)
				hostTuple = (hostname, IP, 'Down')
				self.__listThymiosStates.append(hostTuple)
				self.__logger.info('queryThymios - ' + str(addr) + ' is down')

			for IP in sleepingHosts :
				hostname = getHostnameFromIP(IP)
				hostTuple = (hostname, IP, 'Sleeping')
				self.__listThymiosStates.append(hostTuple)
				self.__logger.info('queryThymios - ' + str(addr) + ' is sleeping')

			for IP in listeningHosts :
				hostname = getHostnameFromIP(IP)
				hostTuple = (hostname, IP, 'Listening')
				self.__listThymiosStates.append(hostTuple)
				self.__logger.info('queryThymios - ' + str(addr) + ' is listening')

			for IP in startedHosts :
				hostname = getHostnameFromIP(IP)
				hostTuple = (hostname, IP, 'Started')
				self.__listThymiosStates.append(hostTuple)
				self.__logger.info('queryThymios - ' + str(addr) + ' is started')


	def launchController(self, controller, detached) :
		try :
			self.__logger.debug('OctoPY - Loading controller...')
			Params.params = Params.Params(controller, self.__logger)

			# We check for the basic parameters
			if Controller.Controller.checkForCompParams() :
				controllerModule = importlib.import_module(Params.params.controller_path)
				controllerClass = getattr(controllerModule, Params.params.controller_name)
				newController = controllerClass(self, detached)
				self.__controllers.append(newController)

				self.__logger.debug('OctoPY - Launching controller...')
				if detached :
					# Threaded execution
					newController.start()
				else :
					newController.run()

			else :
				mainLogger.error('launchController - Couldn\'t load controller, compulsory parameter missing.')
		except :
			self.__logger.error("launchController - Unexpected error : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 

	def registerController(self, controller, IPs) :
		dataObserver = { "ID" : controller.ID }
		self.sendMessage(MessageType.REGISTER, IPs, dataObserver)
	



class OctoPYInteractive(cmd.Cmd) :
	prompt = ">> "

	def logger(self) :
		return octoPYInstance.logger

	# --- Thymios look-up ---
	def do_look(self, args) :
		lookRange = "192.168.0.111-150"
		if args :
			lookRange = args

		octoPYInstance.lookUp(lookRange)

	def help_look(self) :
		print '\n'.join([ 'look [range]', 'Look for all thymios connected on the network in the specified range of IPs (192.168.0.111-150 by default).', ])


	# --- Send message ---
	def do_send(self, args) :
		if args :
			args = args.split(' ')
			message = args[0]

			IPs = []
			if len(args) > 1 :
				IPs = args[1:]

			octoPYInstance.sendMessage(message, IPs)
		else :
			octoPYInstance.logger.critical('sendMessage - No message specified !')

	def complete_send(self, text, line, beidx, endidx) :
		completions = []

		if text :
			if not(text[0].isdigit()) :
				# If the user has begun to type a hostname, we complete it
				if octoPYInstance.hashThymiosHostnames != None :
					completions = [hostname for hostname in octoPYInstance.hashThymiosHostnames.keys() if hostname.startswith(text)]
		else :
			args = line.split(' ')

			if len(args) < 2 or not(args[1].isdigit()) :
				# We propose the list of all the messages
				completions = MessageType.getAllAttributes()
				completions = [str(att[0] + ":" + str(att[1])) for att in completions]
			else :
				# Else we return all the hostnames
				if octoPYInstance.hashThymiosHostnames != None :
					completions = octoPYInstance.hashThymiosHostnames.keys()

		return completions
				


	def help_send(self) :
		print '\n'.join([ 'send message [hosts list]', 'Send a message to a list of hosts or all hosts saved in the hostnames table.'])


	# --- Ping thymios ---
	def do_query(self, args) :
		hosts = []

		if args :
			args = args.split(' ')
			if len(args) > 0 :
				hosts = args

		octoPYInstance.queryThymios(hosts)

	def help_query(self) :
		print '\n'.join([ 'query [hosts list]', 'Query the state of a specified list of hosts or of all host saved in the hostnames table.'])


	# --- Get thymios state ---
	def do_state(self, args) :
		hosts = []

		if args :
			args = args.split(' ')
			if len(args) > 0 :
				hosts = args

		# If listThymiosStates does not exist, we ping the specified thymios to create it
		if octoPYInstance.listThymiosStates == None :
			self.do_query(hosts)

		listStates = []
		# We look for the relevant lines if need be
		if len(hosts) > 0 :
			listIPs = octoPYInstance.resolveAddresses(hosts)
			for IP in listIPs :
				for (hostname, hostIP, state) in octoPYInstance.listThymiosStates :
					if IP == hostIP :
						listStates.append((hostname, hostIP, state))
						break
		else :
			listStates = octoPYInstance.listThymiosStates

		print '\n'.join([ hostname + '\t' + str(IP) + '\t' + state for (hostname, IP, state) in listStates])

	def help_state(self) :
		print '\n'.join([ 'state [hosts lists]', 'Show the state of specified hosts or all hosts saved in the hostnames table.', ])


	# --- Set simulation ---
	def do_set(self, args) :
		if args :
			args = args.split(' ')
			simulation = args[0]

			IPs = []
			if len(args) > 1 :
				IPs = args[1:]

			octoPYInstance.sendMessage(MessageType.SET, IPs, simulation)
		else :
			octoPYInstance.logger.critical('sendMessage - No message specified !')

	def complete_set(self, text, line, beidx, endidx) :
		completions = []
		args = [arg for arg in line.split(' ') if len(arg) > 0]

		if len(args) >= 2 :
			if text :
				# If the user has begun to type a hostname, we complete it
				if octoPYInstance.hashThymiosHostnames != None :
					completions = [hostname for hostname in octoPYInstance.hashThymiosHostnames.keys() if hostname.startswith(text)]
			else :
				# We return all the hostnames
				if octoPYInstance.hashThymiosHostnames != None :
					completions = octoPYInstance.hashThymiosHostnames.keys()

		return completions

	def help_set(self) :
		print '\n'.join(['set simulation [hosts lists]', 'Set the defined simulation for specified hosts or all hosts saved in the hostnames table.'])


	# --- Launch controller ---
	def do_launch(self, args) :
		if args :
			args = args.split(' ')
			controller = args[0]

			detached = False
			if len(args) > 1 :
				if args[1] == '-d' :
					detached = True
				else :
					octoPYInstance.logger.error('launchController - Not a known option : ' + args[1] + '.')

			octoPYInstance.launchController(controller, detached)
		else :
			octoPYInstance.logger.critical('launchController - No controller specified !')

	def help_launch(self) :
		print '\n'.join([ 'launch controller_path [-d detached]', 'Launches a simulation controller.'])


	# --- Exit ---
	def do_exit(self, line) :
		return True

	def help_exit(self) :
		print '\n'.join([ 'exit', 'Exits OctoPY.', ])


	# --- EOF exit ---
	def do_EOF(self, line) :
		return True


if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--look', default = None, const = "192.168.0.111-150", nargs = '?', help = "Look for the alive thymios")
	parser.add_argument('-s', '--send', default = None, nargs = '+', help = "Send a message to a specified thymio or all thymios")
	parser.add_argument('-q', '--query', default = None, nargs = '*', help = "Query the state of a specified thymio or all thymios")
	parser.add_argument('-I', '--interactive', default = False, action = "store_true", help = "Starts OctoPY in interactive mode")
	parser.add_argument('-L', '--log', default = False, action = "store_true", help = "Log messages in a file")
	parser.add_argument('-d', '--debug', default = True, action = "store_true", help = "Debug mode")
	args = parser.parse_args()

	octoPYInstance = OctoPY(args.log, args.debug)

	if args.interactive :
		OctoPYInteractive().cmdloop()
	else :
		if args.look != None :
			octoPYInstance.lookUp(args.look)
		elif args.send != None :
			message = args.send[0]
			IPs = []

			if len(args.send) > 1 :
				IPs = args.send[1:]

			octoPYInstance.sendMessage(message, IPs)
		elif args.query != None :
			IPs = args.query
			octoPYInstance.queryThymios(IPs)
		else :
			octoPYInstance.logger.info("Starting in interactive mode.")
			OctoPYInteractive().cmdloop()
