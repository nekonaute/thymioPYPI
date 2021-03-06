#!/usr/bin/env/python

import io
import sys
import traceback
import logging
from PIL import Image
import cv2
import numpy as np
import time
import re
import xml.dom.minidom
import os
import random
import math

import Simulation
import Params
import Camera

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

PROX_SENSORS_MAX_VALUE = 4500

# Colors detection information
COLORS_DETECT = {
									# "purple" : { 
									# 					"min" : np.array([40, 40, 40]),
									# 					"max" : np.array([80, 255, 255]),
									# 					"input1" : 1,
									# 					"input2" : 0,
									# 					"input3" : 0
									# 				},
									"red" : { 
														"min" : np.array([160, 50, 50]),
														"max" : np.array([180, 255, 255]),
														"input1" : 1,
														"input2" : 1,
														"input3" : 0
														# "input1" : 1,
														# "input2" : 1,
														# "input3" : 0
													},
									"red2" : { 
														"min" : np.array([0, 50, 50]),
														"max" : np.array([20, 255, 255]),
														"input1" : 1,
														"input2" : 1,
														"input3" : 0
														# "input1" : 1,
														# "input2" : 1,
														# "input3" : 0
													},
									"green" : { 
														"min" : np.array([35, 78, 40]),
														# "min" : np.array([32, 40, 40]),
														"max" : np.array([75, 255, 255]),
														"input1" : 1,
														"input2" : 0,
														"input3" : 0
														# "input1" : 0,
														# "input2" : 1,
														# "input3" : 0
													},
									"blue" : { 
														"min" : np.array([90, 50, 50]),
														"max" : np.array([135, 255, 255]),
														"input1" : 0,
														"input2" : 0,
														"input3" : 1
													},
								}


class SimulationStagHunt(Simulation.Simulation) :
	def __init__(self, controller, mainLogger, debug = False) :
		Simulation.Simulation.__init__(self, controller, mainLogger, debug)

		self.__camera = Camera.Camera(mainLogger, COLORS_DETECT)

		# Matrix for the weights from input neurons to hidden neurons
		self.__weightsItoH = None

		# Matrix for the weights from hidden neurons to output neurons
		self.__weightsHtoO = None


	def preActions(self) :
		self.loadWeights(Params.params.weights_path, Params.params.file_xml)
		self.tController.writeColorRequest([32, 32, 32])
		self.waitForControllerResponse()


	def loadWeights(self, file, xmlFile) :
		if os.path.isfile(os.path.join(CURRENT_FILE_PATH, file)) :
			self.log("Loading weights file " + os.path.join(CURRENT_FILE_PATH, file), logging.DEBUG)

			listGenes = []
			if xmlFile == 1:
				DOMTree = xml.dom.minidom.parse(os.path.join(CURRENT_FILE_PATH, file))
				genome = DOMTree.documentElement

				x = genome.getElementsByTagName("x")[0]

				if x :
					best = x.getElementsByTagName("_best")[0]

					if best :
						px = best.getElementsByTagName("px")[0]

						if px :
							gen = px.getElementsByTagName("_gen")[0]

							if gen :
								data = gen.getElementsByTagName("_data")[0]

								listItems = data.getElementsByTagName("item")

								for item in listItems :
									listGenes.append(float(item.childNodes[0].data))
			else :
				regexp = re.compile(r"^(\d+(\.\d+)?)$")
				with open(os.path.join(CURRENT_FILE_PATH, file), 'r') as fileWeights :
					fileWeights = fileWeights.readlines()
					weights = fileWeights[0].rstrip('\n').split(',')

					for weight in weights :
						if len(weight) > 0 :
							gene = float(weight)
							listGenes.append(gene)

			cptColumns = 0
			cptLines = 0
			self.__weightsItoH = np.zeros((Params.params.nb_inputs + 1, Params.params.nb_hidden))
			self.__weightsHtoO = np.zeros((Params.params.nb_hidden + 1, Params.params.nb_outputs))

			for gene in listGenes :
				# Genotype to weights : [0, 1] -> [min_weight, max_weight]
				weight = gene * (float)(Params.params.max_weight - Params.params.min_weight) + Params.params.min_weight

				if cptColumns < Params.params.nb_hidden :
					# We fill the first matrix
					self.__weightsItoH[cptLines, cptColumns] = weight

					cptLines += 1
					if cptLines >= Params.params.nb_inputs + 1 :
						cptLines = 0
						cptColumns += 1
				else :
					# We fill the second matrix
					self.__weightsHtoO[cptLines, cptColumns - (Params.params.nb_hidden)] = weight

					cptLines += 1
					if cptLines >= Params.params.nb_hidden + 1 :
						cptLines = 0
						cptColumns += 1

			# TODO: Remove that at some point
			self.__weightsHtoO2 = np.zeros((Params.params.nb_hidden + 1, Params.params.nb_outputs))
			cptRows = 0
			cptColumns = 0
			cptRows2 = 0
			cptColumns2 = 0
			cpt = 0
			while cpt < ((Params.params.nb_hidden + 1) * Params.params.nb_outputs) :
				self.__weightsHtoO2[cptRows2, cptColumns2] = self.__weightsHtoO[cptRows, cptColumns]

				cptRows += 1
				cptRows2 += 1
				if cptRows >= Params.params.nb_hidden + 1 :
					if cptRows2 >= Params.params.nb_hidden + 1 :
						cptRows -= 1
						cptRows2 = 0
						cptColumns2 = 1
					else :
						cptRows = 0
						cptColumns = 1

				cpt += 1

		else :
			self.log("Weights file " + file + " does not exist.")



	def postActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.tController.writeColorRequest([32, 32, 32])
		self.waitForControllerResponse()


	def getInputs(self) :
		inputs = np.zeros((1, Params.params.nb_inputs + 1))

		index = 0
		index = self.getProximityInputs(inputs, index)

		# self.log("Sensors : ")
		# string = ""
		# for i in range(0, 6) : 
		# 	string += str(inputs[0][i]) + "/"
		# self.log(string)

		index = self.getCameraInputs(inputs, index)

		self.log("Camera : ")
		string = ""
		cpt = 6
		while cpt + 3 <= index :
			if inputs[0][cpt] == 1 and inputs[0][cpt + 1] == 1 and inputs[0][cpt + 2] == 0 :
				string += "Red"
			elif inputs[0][cpt] == 1 and inputs[0][cpt + 1] == 0 and inputs[0][cpt + 2] == 0 :
				string += "Green"
			elif inputs[0][cpt] == 0 and inputs[0][cpt + 1] == 0 and inputs[0][cpt + 2] == 1 :
				string += "Blue"
			else :
				string += "None"
			string += "/"
			cpt += 3

		self.log(string)

		# # TODO: random debug, delete !
		# cpt = 0
		# while cpt < Params.params.nb_inputs :
		# 	inputs[0, cpt] = random.random()
		# 	cpt += 1

		# Bias neuron
		inputs[0, index] = 1.0
		index += 1

		if index != (Params.params.nb_inputs + 1) :
			self.log("SimulationStagHunt - The number of inputs does not correspond to the number of inputs given in parameters.", logging.ERROR)
			return None

		return inputs

	def getProximityInputs(self, inputs, index) :
		try :
			self.tController.readSensorsRequest()
			self.waitForControllerResponse()
			PSValues = self.tController.getPSValues()

			PSToInputs = [4, 5, 0, 1, 2, 3]

			for i in range(0, len(PSValues)) :
				value = float(PSValues[i])/float(PROX_SENSORS_MAX_VALUE)

				if value > 1.0 :
					value = 1.0

				if i == 5 :
					value += float(PSValues[i + 1])/float(PROX_SENSORS_MAX_VALUE)
					value /= 2
					inputs[0, PSToInputs[i]] = value
					index += 1
					break	
				
				inputs[0, PSToInputs[i]] = value

				index += 1
		except :
			self.log('SimulationStagHunt - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
		finally :
			return index

	def getCameraInputs(self, inputs, index) :
		listDetect = self.__camera.detectColors()

		assert(len(listDetect) >= Params.params.nb_rays)
		for i in range(0, Params.params.nb_rays) :
			colorDetected = listDetect[i]

			# self.log("Ray " + str(i) + " : " + colorDetected)
			input1 = 0
			input2 = 0
			input3 = 0
			if colorDetected != 'none' :
				input1 = COLORS_DETECT[colorDetected]['input1']
				input2 = COLORS_DETECT[colorDetected]['input2']
				input3 = COLORS_DETECT[colorDetected]['input3']

			inputs[0, index] = input1
			inputs[0, index + 1] = input2
			inputs[0, index + 2] = input3
			index += 3

		return index

	def computeNN(self, inputs) :
		outputs = [-1.0, -1.0]

		try :
			def sigmoid(x) : return 1.0 / (1.0 + np.exp(-Params.params.lambda_sigmoid * x))

			# First computation : inputs to hidden
			hiddenNN = np.dot(inputs, self.__weightsItoH)
			hiddenNN = np.matrix(map(sigmoid, hiddenNN)).copy()

			# Second computation : hidden to outputs
			# Bias neuron
			hiddenNN.resize((1, Params.params.nb_hidden + 1))
			hiddenNN[0, -1] = 1.0

			outputsNN = np.dot(hiddenNN, self.__weightsHtoO)
			# outputsNN = np.dot(hiddenNN, self.__weightsHtoO2)

			for i in range(0, Params.params.nb_outputs) :
				outputs[i] = sigmoid(outputsNN[0, i])

		except :
			self.log('SimulationStagHunt - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
		finally :
			return outputs

	def step(self) :
		try :
			timeBegStep = time.clock()
			inputs = self.getInputs()
			timeStop = time.clock()
			self.log('Time getInputs : ' + str(timeStop - timeBegStep))

			if inputs != None :
				outputs = self.computeNN(inputs)
				timeStop = time.clock()
				self.log('Time computeNN : ' + str(timeStop - timeBegStep))

				# # TODO: debug
				# self.stop()
				# time.sleep(Params.params.time_step/1000.0)
				# return

				self.log("Outputs :")
				self.log(str(outputs[0]) + "/" + str(outputs[1]))
				if (outputs[0] >= 0) and (outputs[1] >= 0) :
					# vLeft = (outputs[0] * 2.0) - 1.0
					# vRight = (outputs[1] * 2.0) - 1.0
					vRight = (outputs[0] * 2.0) - 1.0
					vLeft = (outputs[1] * 2.0) - 1.0
					self.log("Speed :")
					self.log(str(vLeft) + "/" + str(vRight))
					self.tController.writeMotorsSpeedRequest([vLeft * Params.params.max_speed, vRight * Params.params.max_speed])
					self.waitForControllerResponse()
				else :
					self.tController.writeMotorsSpeedRequest([0.0, 0.0])
					self.waitForControllerResponse()

			time.sleep(Params.params.time_step/1000.0)
		except :
			self.log('SimulationStagHunt - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)


if __name__ == "__main__" :
	# Creation of the logging handlers
	level = logging.DEBUG

	mainLogger = logging.getLogger()
	mainLogger.setLevel(level)

	# File Handler
	fileHandler = logging.FileHandler(os.path.join(CURRENT_FILE_PATH, 'log', 'MainController.log'))
	formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
	fileHandler.setFormatter(formatter)
	fileHandler.setLevel(level)
	mainLogger.addHandler(fileHandler)

	# Console Handler
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(level)
	mainLogger.addHandler(consoleHandler)

	simu = SimulationStagHunt(None, mainLogger, True)
	simu.start()
