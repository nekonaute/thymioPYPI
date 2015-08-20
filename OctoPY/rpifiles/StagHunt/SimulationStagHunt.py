#!/usr/bin/env/python

import picamera
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

import Simulation
import Params

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

PROX_SENSORS_MAX_VALUE = 4500

# Colors detection information
COLORS_DETECT = {
									"purple" : { 
														"min" : np.array([40, 40, 40]),
														"max" : np.array([80, 255, 255]),
														"input1" : 1,
														"input2" : 0,
														"input3" : 0
													},
									"red" : { 
														"min" : np.array([40, 40, 40]),
														"max" : np.array([80, 255, 255])
														"input1" : 1,
														"input2" : 1,
														"input3" : 0
													},
									"green" : { 
														"min" : np.array([40, 40, 40]),
														"max" : np.array([80, 255, 255])
														"input1" : 0,
														"input2" : 1,
														"input3" : 0
													},
								}


class SimulationStagHunt(Simulation.Simulation) :
	def __init__(self, controller, mainLogger, debug = False) :
		Simulation.Simulation.__init__(self, controller, mainLogger, debug)

		self.__camera = picamera.PiCamera()
		self.__camera.resolution = (Params.params.size_x, Params.params.size_y)

		# Matrix for the weights from input neurons to hidden neurons
		self.__weightsItoH = None

		# Matrix for the weights from hidden neurons to output neurons
		self.__weightsHtoO = None


	def preActions(self) :
		self.loadWeights(Params.params.weights_path, Params.params.file_xml)


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

					for line in fileWeights :
						s = regexp.search(line)

						if s :
							gene = float(s.group(1))
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
		else :
			self.log("Weights file " + file + " does not exist.")



	def postActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()


	def getInputs(self) :
		inputs = np.zeros((1, Params.params.nb_inputs + 1))

		# TODO: random debug, delete !
		cpt = 0
		while cpt < Params.params.nb_inputs :
			inputs[0, cpt] = random.random()
			cpt += 1

		index = 0
		# index = self.getProximityInputs(inputs, index)

		# index = self.getCameraInputs(inputs, index)

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

			for i in range(0, len(PSValues)) :
				inputs[0, index + i] = (float)PSValues[i]/(float)PROX_SENSORS_MAX_VALUE
				if inputs[0, index + i] > 1.0 :
					inputs[0, index + i] = 1.0

				index += 1
		except :
			self.log('SimulationStagHunt - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
		finally :
			return index

	def getCameraInputs(self, inputs, index) :
		stream = io.BytesIO()

		# Capture into stream
		self.__camera.capture(stream, 'jpeg', use_video_port = True)
		data = np.fromstring(stream.getvalue(), dtype = np.uint8)
		img = cv2.imdecode(data, 1)

		# We take just a group of lines from the image
		firstLine = (int)((1.0 - Params.params.view_height)*Params.params.size_y) - Params.params.ray_height_radius
		lastLine = firstLine + Params.params.ray_height_radius + 1
		imgReduced = img[firstLine:(lastLine + 1)]

		# Blurring and converting to HSV values
		imgReduced = cv2.GaussianBlur(imgReduced, (5, 5), 0)
		imgHSV = cv2.cvtColor(imgReduced, cv2.COLOR_BGR2HSV)

		# We separate the images in rays
		imgRays =  []
		increment = math.floor(Params.params.size_x/Params.params.nb_rays)
		rayX = Params.params.ray_width_radius
		for i in range(0, Params.params.nb_rays) :
			if rayX < Params.params.size_x :
				firstColumn = rayX - Params.params.ray_width_radius
				lastColumn = rayX + Params.params.ray_width_radius

				if lastColumn >= Params.params.size_x :
					lastColumn = Params.params.size_x

				tmpArray = []
				cpt = 0

				while cpt < len(imgHSV) :
					tmpArray.append(imgHSV[cpt][firstColumn:(lastColumn + 1)])
					cpt += 1

				imgRays.append(np.array(tmpArray))

			rayX += increment


		# We get masks according to each color we want to find
		listMasks = []
		countDetect = []
		listDetect = []
		for ray in imgRays :
			hashMasks = {}
			hashDetect = {}
			maxDetect = 0
			listDetect.append('none')

			for color in COLORS_DETECT :
				mask = cv2.inRange(ray, COLORS_DETECT[color]['min'], COLORS_DETECT[color]['max'])
				# mask = cv2.GaussianBlur(mask, (5, 5), 0)
				hashMasks[color] = mask

				# We count the number of 1 in the mask (color detected)
				nbDetect = np.count_nonzero(mask)
				hashDetect[color] = nbDetect

				# If more than 50% of the mask are ones
				if nbDetect > ((Params.params.ray_width_radius + 1) * (Params.params.ray_height_radius + 1))/2 :
					if nbDetect > maxDetect :
						maxDetect = nbDetect
						listDetect[-1] = color


			countDetect.append(hashDetect)
			listMasks.append(hashMasks)

			# We set the inputs for this ray
			colorDetected = listDetect[-1]

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

			for i in range(0, Params.params.nb_outputs) :
				outputs[i] = sigmoid(outputsNN[0, i])

		except :
			self.log('SimulationStagHunt - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
		finally :
			return outputs

	def step(self) :
		try :
			inputs = self.getInputs()

			if inputs != None :
				outputs = self.computeNN(inputs)

				if (outputs[0] >= 0) and (outputs[1] >= 0) :
					self.tController.writeMotorsSpeedRequest([outputs[0] * Params.params.max_speed, outputs[1] * Params.params.max_speed])
					self.waitForControllerResponse()
				else :
					self.tController.writeMotorsSpeedRequest([0.0, 0.0])
					self.waitForControllerResponse

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