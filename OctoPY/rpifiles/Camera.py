import picamera
import traceback
import os
import sys
import logging
import cv2
from PIL import Image
import numpy as np
import time
import io
import math

import Params


class Camera() :
	def __init__(self, mainLogger, colorDetect) :
		self.__camera = picamera.PiCamera()
		self.__camera.resolution = (Params.params.size_x, Params.params.size_y)

		self.__colorDetect = colorDetect
		self.__mainLogger = mainLogger

		# We need to let time for the camera to load
		time.sleep(3)

	def detectColors(self) :
		listDetect = []
		# timeBegTotal = time.clock()

		try :
			stream = io.BytesIO()

			# Capture into stream
			# timeBegStep = time.clock()
			self.__camera.capture(stream, 'jpeg', use_video_port = True)
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time capture : ' + str(timeStop - timeBegStep))

			# timeBegStep = time.clock()
			data = np.fromstring(stream.getvalue(), dtype = np.uint8)
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time fromstring : ' + str(timeStop - timeBegStep))

			# timeBegStep = time.clock()
			img = cv2.imdecode(data, 1)
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time imdecode : ' + str(timeStop - timeBegStep))

			# cv2.imwrite("./imgBase.jpg", img)

			# Blurring and converting to HSV values
			# imgHSV2 = cv2.GaussianBlur(img, (5, 5), 0)
			# imgHSV2 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			# cv2.imwrite("./imgHSV.jpg", imgHSV2)

			# We take just a group of lines from the image
			# timeBegStep = time.clock()
			firstLine = (int)((1.0 - Params.params.view_height)*Params.params.size_y) - Params.params.ray_height_radius
			lastLine = firstLine + 2*Params.params.ray_height_radius
			imgReduced = img[firstLine:(lastLine + 1)]
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time pre-treatment : ' + str(timeStop - timeBegStep))

			# cv2.imwrite("./imgReduced.jpg", imgReduced)

			# Blurring and converting to HSV values
			# timeBegStep = time.clock()
			imgReduced = cv2.GaussianBlur(imgReduced, (5, 5), 0)
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time gaussian blur : ' + str(timeStop - timeBegStep))

			# timeBegStep = time.clock()
			imgHSV = cv2.cvtColor(imgReduced, cv2.COLOR_BGR2HSV)
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time cvtColor : ' + str(timeStop - timeBegStep))

			# cv2.imwrite("./imgHSVReduced.jpg", imgHSV)

			# We separate the images in rays
			# timeBegStep = time.clock()
			imgRays =  []
			increment = math.floor(Params.params.size_x/(Params.params.nb_rays - 1))
			compensation = Params.params.size_x - ((Params.params.nb_rays - 1) * increment)
			rayX = math.floor(compensation/2)
			for i in range(0, Params.params.nb_rays) :
				if rayX < Params.params.size_x :
					firstColumn = rayX - Params.params.ray_width_radius
					lastColumn = rayX + Params.params.ray_width_radius

					if firstColumn < 0 :
						firstColumn = 0
						lastColumn = 2 * Params.params.ray_width_radius

					if lastColumn >= Params.params.size_x :
						firstColumn = Params.params.size_x - 2 * Params.params.ray_width_radius
						lastColumn = Params.params.size_x - 1

					tmpArray = []
					cpt = 0

					while cpt < len(imgHSV) :
						tmpArray.append(imgHSV[cpt][firstColumn:(lastColumn + 1)])
						cpt += 1

					imgRays.append(np.array(tmpArray))

				rayX += increment		

			# timeStop = time.clock()
			# self.__mainLogger.debug('Time rays treatment : ' + str(timeStop - timeBegStep))

			# We get masks according to each color we want to find
			# timeBegStep = time.clock()
			listMasks = []
			countDetect = []
			cpt = 1
			for ray in imgRays :
				# self.__mainLogger.debug('Ray : ' + str(cpt))
				hashMasks = {}
				hashDetect = {}
				maxDetect = 0
				listDetect.append('none')

				# self.__mainLogger.debug("Ray " + str(cpt) + " : " + str(ray))

				for color in self.__colorDetect :
					mask = cv2.inRange(ray, self.__colorDetect[color]['min'], self.__colorDetect[color]['max'])
					# self.__mainLogger.debug("Mask : " + str(mask))
					# mask = cv2.GaussianBlur(mask, (5, 5), 0)
					hashMasks[color] = mask

					# We count the number of 1 in the mask (color detected)
					nbDetect = np.count_nonzero(mask)
					hashDetect[color] = nbDetect

					# If more than 50% of the mask are ones
					# self.__mainLogger.debug('Color : ' + str(color) + ", nbDetect : " + str(nbDetect))
					if nbDetect > ((Params.params.ray_width_radius + 1) * (Params.params.ray_height_radius + 1))/2 :
						if nbDetect > maxDetect :
							maxDetect = nbDetect
							listDetect[-1] = color

				# self.__mainLogger.debug('Color detected : ' + str(listDetect[-1]))


				countDetect.append(hashDetect)
				listMasks.append(hashMasks)

				cpt += 1
			# timeStop = time.clock()
			# self.__mainLogger.debug('Time masks treatment : ' + str(timeStop - timeBegStep))

			# timeStopTotal = time.clock()
			# self.__mainLogger.debug('Total time : ' + str(timeStopTotal - timeBegTotal))
		except :
			self.__mainLogger.critical('Camera - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
		finally :
			return listDetect


if __name__ == "__main__" :
	# Creation of the logging handlers
	level = logging.DEBUG

	mainLogger = logging.getLogger()
	mainLogger.setLevel(level)

	# Console Handler
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(level)
	mainLogger.addHandler(consoleHandler)

	camera = Camera(mainLogger, None)
	camera.detectColors()