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

from utils import *

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

HOSTNAMES_TABLE_FILE_PATH = os.path.join(CURRENT_FILE_PATH, 'hostnames_table.json')

LOG_PATH = os.path.join(CURRENT_FILE_PATH, 'log', 'medusa.log')

THYMIO_SCRIPTS_PATH = '/home/pi/dev/thymioPYPI/amsterdam/thymio_exchange_seq/scripts'

PIUSERNAME = 'pi'
PIPASSWORD = 'pi'

ACKLISTENER_HOST = ''
ACKLISTENER_PORT = 55555

TIMEOUT_ACK = 10
TIMEOUT_QUERY = 5

logger = None
hashThymiosHostnames = None



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


def queryThymios(options) :
	try :
		logger.info("queryThymios - excuting nmap")

		# Popen calls the nmap command in the range specified by options.look
		proc = subprocess.Popen(["nmap", "-sn", options.look], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		(out, err) = proc.communicate()

		if proc.returncode < 0 :
			logger.error("queryThymios - Error executing nmap : " + str(err))
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

		logger.info("queryThymios - nmap done")

		if len(tabIP) == 0 :
			logger.info("queryThymios - no up thymios were found !")
			return

		logger.debug("queryThymios - IP address for up thymios found :")
		for IP in tabIP :
			logger.debug("\t " + str(IP))

		logger.info("queryThymios - Gathering thymios' hostnames")

		global hashThymiosHostnames
		hashThymiosHostnames = {}

		# We query each thymio for its hostname
		for IP in tabIP :
			logger.info("queryThymios - ssh on " + str(IP))

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

			logger.info("queryThymios - active thymio: " + hostname + " - " + str(IP))

			if hostname in hashThymiosHostnames.keys() :
				logger.warning("queryThymios - warning: multiple thymios with hostname " + hostname + " : " + str(hashThymiosHostnames[hostname]) + " and " + str(IP))

			hashThymiosHostnames[hostname] = IP

		logger.debug("queryThymios - hostname/IP table :")
		for hostname in hashThymiosHostnames :
			logger.debug("\t " + hostname + " : " + str(hashThymiosHostnames[hostname]))

		saveHostnamesTable()

	except :	
		logger.critical("Unexpected error in queryThymios : " + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc()) 


def sendMessage(options) :
	# We first load the hostnames table (if it exists)
	if os.path.isfile(HOSTNAMES_TABLE_FILE_PATH) :
		loadHostnamesTable()
	else :
		logging.warning("sendMessage - there is no hostnames table")

	# Message
	message = int(options.send[0])

	# List of recipients
	dest = []
	if len(options.send) > 1 :
		recipList = options.send[1:]

		logging.debug("sendMessage - recipients list : " + ' '.join(recipList))

		# Resolution of hostnames to IP address
		for recip in recipList :
			if hashThymiosHostnames != None and recip in hashThymiosHostnames.keys() :
				dest.append(hashThymiosHostnames[recip])
			else :
				# We verify that this is a correct IP address
				try :
					dest.append(ipaddress.ip_address(u'' + recip))
				except :
					logging.error("sendMessage - " + recip + " is not a known host nor a valid IP address")
					continue
	else :
		# If no host was specified, we send to every known hosts
		if hashThymiosHostnames != None :
			dest = [ipaddress.ip_address(u'' + IP) for IP in hashThymiosHostnames.values()]
		else :
			logging.critical("sendMessage - No hosts specified and no existing hostnames table")
			exit(1)

	
	myIP = None

	sockACK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockACK.setblocking(0)
	sockACK.bind((ACKLISTENER_HOST, ACKLISTENER_PORT))
	sockACK.listen(5)

	waitingACK = []
	for destIP in dest :
		logging.info("sendMessage - sending message " + str(message) + " to " + str(destIP))

		optSend = DirtyMessage()

		try :
			# Init thymio
			if message == MessageType.INIT :
				ssh = paramiko.SSHClient()
				ssh.load_system_host_keys()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

				# We don't want to be bothered with paramiko logging unless it's critical
				paramikoLogger = logging.getLogger('paramiko')
				paramikoLogger.setLevel('CRITICAL')

				# Connection on the raspberry
				ssh.connect(str(destIP), username = PIUSERNAME, password = PIPASSWORD)

				# We get our IP address on this network
				if myIP == None :
					stdin, stdout, stderr = ssh.exec_command('echo $SSH_CLIENT')
					myIP = ipaddress.ip_address(u'' + stdout.read().split(' ')[0])

				# Executing command hostname
				stdin, stdout, stderr = ssh.exec_command('sh ' + os.path.join(THYMIO_SCRIPTS_PATH, '_init_thymio.sh') + ' ' + str(myIP))

				ssh.close()

				waitingACK.append(str(destIP))

			# Start simulation
			elif message == MessageType.START :
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((str(destIP), 55555))
				sendOneMessage(sock, optSend)

			# Stop simulation
			elif message == MessageType.STOP :
				optSend.running = False
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((str(destIP), 55555))
				sendOneMessage(sock, optSend)

			# Kill thymio
			elif message == MessageType.KILL :
				optSend.kill = True
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((str(destIP), 55555))
				sendOneMessage(sock, optSend)

			else :
				logging.critical("sendMessage - not a known message id : " + str(message))
				exit(1)
		except :
			logging.error("sendMessage - Unexpected error while sending message " + str(message) + " to " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
			continue

	# Waiting for ACK
	if message == MessageType.INIT :
		timeOut = TIMEOUT_ACK
		while len(waitingACK) > 0 :
			logging.debug('sendMessage - Waiting ACK from ' + ' '.join(waitingACK))
			readable, writable, exceptional = select.select([sockACK], [], [], timeOut)

			# If a timeout happend
			if not (readable or writable or exceptional) :
				logging.warning('sendMessage - No ACK from ' + ' '.join(waitingACK) + ' after ' + str(timeOut) + ' seconds')
				break
			else :
				for sock in readable :
					conn, (addr, port) = sock.accept()
					logging.debug('sendMessage - Receiving message from ' + str(addr))

					data = recvOneMessage(conn)
					if data.message == MessageType.ACK :
						logging.info('sendMessage - ACK received from ' + str(addr))
						waitingACK.remove(addr)


def ping(options) :
	# We first load the hostnames table (if it exists)
	if os.path.isfile(HOSTNAMES_TABLE_FILE_PATH) :
		loadHostnamesTable()
	else :
		logging.warning("ping - there is no hostnames table")

	# List of recipients
	dest = []
	if len(options.send) > 0 :
		recipList = options.send

		logging.debug("ping - recipients list : " + ' '.join(recipList))

		# Resolution of hostnames to IP address
		for recip in recipList :
			if hashThymiosHostnames != None and recip in hashThymiosHostnames.keys() :
				dest.append(hashThymiosHostnames[recip])
			else :
				# We verify that this is a correct IP address
				try :
					dest.append(ipaddress.ip_address(u'' + recip))
				except :
					logging.error("ping - " + recip + " is not a known host nor a valid IP address")
					continue
	else :
		# If no host was specified, we send to every known hosts
		if hashThymiosHostnames != None :
			dest = [ipaddress.ip_address(u'' + IP) for IP in hashThymiosHostnames.values()]
		else :
			logging.critical("ping - No hosts specified and no existing hostnames table")
			exit(1)

	try :
		newDest = dest
		for destIP in dest :
			# We first ping each recipient
			logging.info("ping - pinging " + str(destIP))
			proc = subprocess.Popen(['ping', str(destIP), '-c1', '-W2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			(stdout, stderr) = proc.communicate()[0]
			
			if proc.returncode != 0 :
				logging.info("ping - " + str(destIP) + " is not up")
				newDest.remove(destIP)
			else :
				logging.info("ping - " + str(destIP) + " is up")

		dest = newDest
	except :
		logging.critical("ping - Unexpected error while pinging " + str(destIP))
		exit(1)


	waitingAnswer = []
	sockAnswer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockAnswer.setblocking(0)
	sockAnswer.bind((ACKLISTENER_HOST, ACKLISTENER_PORT))
	sockAnswer.listen(5)

	try :

		optSend = DirtyMessage()
		optSend.message = MessageType.QUERY
		for destIP in dest :
			# We send a message to each recipient
			logging.info("ping - sending query to " + str(destIP))
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((str(destIP), 55555))
			sendOneMessage(sock, optSend)
			waitingAnswer.append(str(destIP))
	except :
			logging.error("ping - Unexpected error while sending query to " + str(destIP) + " : " + str(sys.exc_info()[0]) + " - " + traceback.format_exc()) 
			continue


	# Waiting for answers
	timeOut = TIMEOUT_QUERY
	listeningHosts = []
	startedHosts = []
	sleepingHosts = []
	while len(waitingAnswer) > 0 :
		logging.debug('ping - Waiting answer from ' + ' '.join(waitingAnswer))
		readable, writable, exceptional = select.select([sockAnswer], [], [], timeOut)

		# If a timeout happend
		if not (readable or writable or exceptional) :
			logging.debug('ping - No answer from ' + ' '.join(waitingAnswer) + ' after ' + str(timeOut) + ' seconds')
			sleepingHosts = waitingAnswer
			break
		else :
			for sock in readable :
				conn, (addr, port) = sock.accept()
				logging.debug('ping - Receiving message from ' + str(addr))

				data = recvOneMessage(conn)
				if data.message == MessageType.LISTENING :
					logging.debug('ping - LISTENING received from ' + str(addr))
					waitingAnswer.remove(addr)
					listeningHosts.append(addr)
				elif data.message == MessageType.STARTED :
					logging.debug('ping - STARTED received from ' + str(addr))
					waitingAnswer.remove(addr)
					startedHosts.append(addr)
				else :
					logging.error("ping - not an expected message " + str(message) + " from " + str(addr))
					waitingAnswer.remove(addr)
					continue

	for IP in sleepingHosts :
		logging.info('ping - ' + str(addr) + ' is sleeping')
	for IP in listeningHosts :
		logging.info('ping - ' + str(addr) + ' is listening')
	for IP in startedHosts :
		logging.info('ping - ' + str(addr) + ' is started')







if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--look', default = None, const = "192.168.0.111-150", nargs = '?', help = "Look for the alive thymios")
	parser.add_argument('-s', '--send', default = None, nargs = '+', help = "Send a message to a specified thymio or all thymios")
	parser.add_argument('-p', '--ping', default = None, nargs = '*', help = "Get the state of a specified thymio or all thymios")
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

	if args.look != None :
		queryThymios(args)
	elif args.send != None :
		sendMessage(args)
	elif args.ping != None :
		ping(args)
	else :
		logger.error("No query specified !")
