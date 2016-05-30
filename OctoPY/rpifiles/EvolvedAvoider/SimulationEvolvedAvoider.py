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
import math

import Simulation
import Params

CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

PROX_SENSORS_MAX_VALUE = 4500

class SimulationEvolvedAvoider(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		# Matrix for the weights from input neurons to output neurons
		self.__weightsItoH = None


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
					weights = fileWeights.rstrip('\n').split(',')

					for weight in weights :
						if len(weight) > 0 :
							gene = float(weight)
							listGenes.append(gene)


			cptColumns = 0
			cptLines = 0
			self.__weightsItoO = np.zeros((Params.params.in_inputs + 1, Params.params.nb_outputs))

			for gene in listGenes :
				assert(cptColumns < Params.params.nb_outputs)

				# Genotype to weights : [0, 1] -> [min_weight, max_weight]
				weight = gene * (float)(Params.params.max_weight - Params.params.min_weight) + Params.params.min_weight

				self.__weightsItoO[cptLines, cptColumns] = weight
				cptLines += 1
				if cptLines >= Params.params.nb_inputs + 1 :
					cptLines = 0
					cptColumns += 1
		else :
			self.log("Weights file " + file + " does not exist.")

	def postActions(self) :
		self.tController.writeMotorsSpeedRequest([0, 0])
		self.waitForControllerResponse()


	def getInputs(self) :
		inputs = np.zeros((1, Params.params.nb_inputs + 1))

		index = 0
		index = self.getProximityInputs(inputs, index)

		# self.log("Inputs : ")
		# self.log(inputs)

		# Bias neuron
		inputs[0, index] = 1.0
		index += 1

		if index != (Params.params.nb_inputs + 1) :
			self.log("SimulationEvolvedAvoider - The number of inputs does not correspond to the number of inputs given in parameters.", logging.ERROR)
			return None

		return inputs

	def getProximityInputs(self, inputs, index) :
		try :
			self.tController.readSensorsRequest()
			self.waitForControllerResponse()
			PSValues = self.tController.getPSValues()

			# for i in range(0, len(PSValues)) :
			for i in range(0, Params.params.nb_prox) :
				inputs[0, index + i] = (float)(PSValues[i])/(float)(PROX_SENSORS_MAX_VALUE)
				if inputs[0, index + i] > 1.0 :
					inputs[0, index + i] = 1.0

				index += 1

			# self.log("Proximity sensors :")
			# self.log(PSValues)
		except :
			self.log('SimulationEvolvedAvoider - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
		finally :
			return index

	def computeNN(self, inputs) :
		outputs = [-1.0, -1.0]

		try :
			def sigmoid(x) : return 1.0 / (1.0 + np.exp(-Params.params.lambda_sigmoid * x))

			outputsNN = np.dot(inputs, self.__weightsItoO)

			for i in range(0, Params.params.nb_outputs) :
				outputs[i] = sigmoid(outputsNN[0, i])

		except :
			self.log('SimulationEvolvedAvoider - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
		finally :
			return outputs

	def step(self) :
		try :
			inputs = self.getInputs()

			if inputs != None :
				outputs = self.computeNN(inputs)

				# # TODO: debug
				# self.stop()
				# time.sleep(Params.params.time_step/1000.0)
				# return

				if (outputs[0] >= 0) and (outputs[1] >= 0) :
					self.tController.writeMotorsSpeedRequest([outputs[0] * Params.params.max_speed, outputs[1] * Params.params.max_speed])
					self.waitForControllerResponse()
				else :
					self.tController.writeMotorsSpeedRequest([0.0, 0.0])
					self.waitForControllerResponse

			time.sleep(Params.params.time_step/1000.0)
		except :
			self.log('SimulationEvolvedAvoider - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc(), logging.CRITICAL)
