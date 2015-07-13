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

import ipaddress
import paramiko
import cmd

import utils
from utils import recvall, recvOneMessage, sendOneMessage, MessageType

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

HOSTNAMES_TABLE_FILE_PATH = os.path.join(CURRENT_FILE_PATH, 'hostnames_table.json')

LOG_PATH = os.path.join(CURRENT_FILE_PATH, 'log', 'thymioControl.log')

THYMIO_SCRIPTS_PATH = '/home/pi/dev/thymioPYPI/medusa/rpifiles'

PIUSERNAME = 'pi'
PIPASSWORD = 'pi'

LISTENER_HOST = ''
LISTENER_PORT = 55555

TIMEOUT_ACK = 10
TIMEOUT_QUERY = 5

logger = None
hashThymiosHostnames = None
listThymiosStates = None



def saveHostnamesTable() :
	logger.info("saveHostnamesTable - Saving hostnames table")

	if hashThymiosHostnames != None :
		try :
			with open(HOSTNAMES_TABLE_FILE_PATH, 'w') as fileOutput :
				json.dump(hashThymiosHostnames, fileOutput)
		except :
			logger.critical("Unexpected error in saveHostnamesTable : " + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc()) 
	else :
		logger.error("No table created")

def loadHostnamesTable() :
	logger.info("loadHostnamesTable - Loading hostnames table")

	try :
		global hashThymiosHostnames

		with open(HOSTNAMES_TABLE_FILE_PATH, 'r') as fileInput :
			hashThymiosHostnames = json.load(fileInput)

		logger.debug("loadHostnamesTable - hostnames table :")
		for hostname in hashThymiosHostnames :
			logger.debug("\t " + hostname + " : " + str(hashThymiosHostnames[hostname]))
	except :
		logger.critical("Unexpected error in loadHostnamesTable : " + str(sys.exc_info()[0]) + ' - ' +traceback.format_exc())


def lookUp(rangeArg) :
	try :
		logger.info("lookUp - excuting nmap")

		# Popen calls the nmap command in the range specified by rangeArg
		proc = subprocess.Popen(["nmap", "-sn", rangeArg], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		(out, err) = proc.communicate()

		if proc.returncode < 0 :
			logger.error("lookUp - Error executing nmap : " + str(err))
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

		logger.info("lookUp - nmap done")

		if len(tabIP) == 0 :
			logger.info("lookUp - no up thymios were found !")
			return

		logger.debug("lookUp - IP address for up thymios found :")
		for IP in tabIP :
			logger.debug("\t " + str(IP))

		logger.info("lookUp - Gathering thymios' hostnames")

		global hashThymiosHostnames
		hashThymiosHostnames = {}

		# We query each thymio for its hostname
		for IP in tabIP :
			logger.info("lookUp - ssh on " + str(IP))

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

			logger.info("lookUp - active thymio: " + hostname + " - " + str(IP))

			if hostname in hashThymiosHostnames.keys() :
				logger.warning("lookUp - warning: multiple thymios with hostname " + hostname + " : " + str(hashThymiosHostnames[hostname]) + " and " + str(IP))

			hashThymiosHostnames[hostname] = IP

		logger.debug("lookUp - hostname/IP table :")
		for hostname in hashThymiosHostnames :
			logger.debug("\t " + hostname + " : " + str(hashThymiosHostnames[hostname]))

		saveHostnamesTable()

	except :	
		logger.critical("Unexpected error in lookUp : " + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc()) 


def getHostnameFromIP(IP) :
	if hashThymiosHostnames :
		for hostname in hashThymiosHostnames.keys() :
			if hashThymiosHostnames[hostname] == IP :
				return hostname

	return None

def resolveAddresses(IPs) :
	# List of recipients
	dest = []
	if len(IPs) > 0 :
		recipList = IPs

		logging.debug("resolveAddresses - recipients list : " + ' '.join(recipList))

		# Resolution of hostnames to IP address
		for recip in recipList :
			if hashThymiosHostnames != None and recip in hashThymiosHostnames.keys() :
				dest.append(hashThymiosHostnames[recip])
			else :
				# We verify that this is a correct IP address
				try :
					dest.append(ipaddress.ip_address(u'' + recip))
				except :
					logging.error("resolveAddresses - " + recip + " is not a known host nor a valid IP address")
					continue
	else :
		# If no host was specified, we send to every known hosts
		if hashThymiosHostnames != None :
			dest = [ipaddress.ip_address(u'' + IP) for IP in hashThymiosHostnames.values()]
		else :
			logging.critical("resolveAddresses - No hosts specified and no existing hostnames table")
			return None

	return dest


def sendMessage(message, IPs) :
	# Message
	message = int(message)

	# Addresses resolution
	dest = resolveAddresses(IPs)

	myIP = None
	if dest != None :
		# sockACK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# sockACK.setblocking(0)
		# sockACK.bind((ACKLISTENER_HOST, ACKLISTENER_PORT))
		# sockACK.listen(5)

		for destIP in dest :
			logging.info("sendMessage - sending message " + str(message) + " to " + str(destIP))

			optSend = utils.Message()

			try :
				# Init thymio
				if message == MessageType.INIT :
					# ssh = paramiko.SSHClient()
					# ssh.load_system_host_keys()
					# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

					# # We don't want to be bothered with paramiko logging unless it's critical
					# paramikoLogger = logging.getLogger('paramiko')
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
					proc = subprocess.Popen(sshcommand + ["asebamedulla", "ser:device=/dev/ttyACM0", "&", "python", os.path.join(THYMIO_SCRIPTS_PATH, 'exchange_seq.py'), '-d', '-i', str(myIP), '&'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
					# proc = subprocess.Popen(sshcommand + ["sh", os.path.join(THYMIO_SCRIPTS_PATH, '_init_thymio.sh'), str(myIP)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
					# proc.wait()

				# Start simulation
				elif message == MessageType.START :
					optSend.msgType = MessageType.START
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

				else :
					logging.critical("sendMessage - not a known message id : " + str(message))
					return
			except :
				logging.error("sendMessage - Unexpected error while sending message " + str(message) + " to " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
				continue


def queryThymios(IPs) :
	dest = resolveAddresses(IPs)

	if dest != None :
		try :
			newDest = dest
			downHosts = []
			for destIP in dest :
				# We first ping each recipient
				logging.info("queryThymios - pinging " + str(destIP))
				proc = subprocess.Popen(['ping', str(destIP), '-c1', '-W2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				(stdout, stderr) = proc.communicate()
				
				if proc.returncode != 0 :
					logging.info("queryThymios - " + str(destIP) + " is not up")
					downHosts.append(destIP)
					newDest.remove(destIP)
				else :
					logging.info("queryThymios - " + str(destIP) + " is up")

			dest = newDest
		except :
			logging.critical("queryThymios - Unexpected error while pinging " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc())
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
				logging.info("queryThymios - sending query to " + str(destIP))
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((str(destIP), 55555))
				sendOneMessage(sock, optSend)
				waitingAnswer.append(str(destIP))
			except :
				logging.error("queryThymios - Unexpected error while sending query to " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
				continue


		# Waiting for answers
		timeOut = TIMEOUT_QUERY
		listeningHosts = []
		startedHosts = []
		sleepingHosts = []
		while len(waitingAnswer) > 0 :
			logging.debug('queryThymios - Waiting answer from ' + ' '.join(waitingAnswer))
			readable, writable, exceptional = select.select([sockAnswer], [], [], timeOut)

			# If a timeout happend
			if not (readable or writable or exceptional) :
				logging.debug('queryThymios - No answer from ' + ' '.join(waitingAnswer) + ' after ' + str(timeOut) + ' seconds')
				sleepingHosts = waitingAnswer
				break
			else :
				for sock in readable :
					conn, (addr, port) = sock.accept()
					logging.debug('queryThymios - Receiving message from ' + str(addr))

					data = recvOneMessage(conn)
					if data.message == MessageType.LISTENING :
						logging.debug('queryThymios - LISTENING received from ' + str(addr))
						waitingAnswer.remove(addr)
						listeningHosts.append(addr)
					elif data.message == MessageType.STARTED :
						logging.debug('queryThymios - STARTED received from ' + str(addr))
						waitingAnswer.remove(addr)
						startedHosts.append(addr)
					else :
						logging.error("queryThymios - not an expected message " + str(message) + " from " + str(addr))
						waitingAnswer.remove(addr)
						continue

		global listThymiosStates
		listThymiosStates = []
		for IP in downHosts :
			hostname = getHostnameFromIP(IP)
			hostTuple = (hostname, IP, 'Down')
			listThymiosStates.append(hostTuple)
			logging.info('queryThymios - ' + str(addr) + ' is down')

		for IP in sleepingHosts :
			hostname = getHostnameFromIP(IP)
			hostTuple = (hostname, IP, 'Sleeping')
			listThymiosStates.append(hostTuple)
			logging.info('queryThymios - ' + str(addr) + ' is sleeping')

		for IP in listeningHosts :
			hostname = getHostnameFromIP(IP)
			hostTuple = (hostname, IP, 'Listening')
			listThymiosStates.append(hostTuple)
			logging.info('queryThymios - ' + str(addr) + ' is listening')

		for IP in startedHosts :
			hostname = getHostnameFromIP(IP)
			hostTuple = (hostname, IP, 'Started')
			listThymiosStates.append(hostTuple)
			logging.info('queryThymios - ' + str(addr) + ' is started')



class MedusaInteractive(cmd.Cmd) :
	prompt = ">> "


	# --- Thymios look-up ---
	def do_look(self, args) :
		lookRange = "192.168.0.111-150"
		if args :
			lookRange = args

		lookUp(lookRange)

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

			sendMessage(message, IPs)
		else :
			logging.critical('sendMessage - No message specified !')

	def complete_send(self, text, line, beidx, endidx) :
		completions = []

		if text :
			if not(text[0].isdigit()) :
				# If the user has begun to type a hostname, we complete it
				if hashThymiosHostnames != None :
					completions = [hostname for hostname in hashThymiosHostnames.keys() if hostname.startswith(text)]
		else :
			args = line.split(' ')

			if args < 2 or not(args[1].isdigit()) :
				# We propose the list of all the messages
				completions = MessageType.getAllAttributes()
				completions = [str(att[0] + ":" + str(att[1])) for att in completions]
			else :
				# Else we return all the hostnames
				if hashThymiosHostnames != None :
					completions = hashThymiosHostnames.keys()

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

		queryThymios(hosts)

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
		if listThymiosStates == None :
			self.do_query(hosts)

		listStates = []
		# We look for the relevant lines if need be
		if len(hosts) > 0 :
			listIPs = resolveAddresses(hosts)
			for IP in listIPs :
				for (hostname, hostIP, state) in listThymiosStates :
					if IP == hostIP :
						listStates.append((hostname, hostIP, state))
						break
		else :
			listStates = listThymiosStates

		print '\n'.join([ hostname + '\t' + str(IP) + '\t' + state for (hostname, IP, state) in listStates])

	def help_state(self) :
		print '\n'.join([ 'state [hosts lists]', 'Show the state of specified hosts or all hosts saved in the hostnames table.', ])


	# --- Exit ---
	def do_exit(self, line) :
		return True

	def help_exit(self) :
		print '\n'.join([ 'exit', 'Exits medusa.', ])


	# --- EOF exit ---
	def do_EOF(self, line) :
		return True


if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--look', default = None, const = "192.168.0.111-150", nargs = '?', help = "Look for the alive thymios")
	parser.add_argument('-s', '--send', default = None, nargs = '+', help = "Send a message to a specified thymio or all thymios")
	parser.add_argument('-q', '--query', default = None, nargs = '*', help = "Query the state of a specified thymio or all thymios")
	parser.add_argument('-I', '--interactive', default = False, action = "store_true", help = "Starts medusa in interactive mode")
	parser.add_argument('-L', '--log', default = False, action = "store_true", help = "Log messages in a file")
	parser.add_argument('-d', '--debug', default = True, action = "store_true", help = "Debug mode")
	args = parser.parse_args()

	# Creation of the logging handlers
	level = logging.INFO
	if args.debug :
		level = logging.DEBUG

	logger = logging.getLogger()
	logger.setLevel(level)

	# File Handler
	if args.log :
		fileHandler = logging.FileHandler(LOG_PATH)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
		fileHandler.setFormatter(formatter)
		fileHandler.setLevel(level)
		logger.addHandler(fileHandler)

	# Console Handler
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(level)
	logger.addHandler(consoleHandler)

	# We load the hostnames table (if it exists)
	if os.path.isfile(HOSTNAMES_TABLE_FILE_PATH) :
		loadHostnamesTable()
	else :
		logging.debug("No existing hostnames table found")


	if args.interactive :
		MedusaInteractive().cmdloop()
	else :
		if args.look != None :
			lookUp(args.look)
		elif args.send != None :
			message = args.send[0]
			IPs = []

			if len(args.send) > 1 :
				IPs = args.send[1:]

			sendMessage(message, IPs)
		elif args.query != None :
			IPs = args.query
			queryThymios(IPs)
		else :
			logger.error("No query specified !")
