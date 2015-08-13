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

		try :
			stream = io.BytesIO()

			# Capture into stream
			self.__camera.capture(stream, 'jpeg', use_video_port = True)
			data = np.fromstring(stream.getvalue(), dtype = np.uint8)
			img = cv2.imdecode(data, 1)

			cv2.imwrite("./imgBase.jpg", img)

			# Blurring and converting to HSV values
			# imgHSV2 = cv2.GaussianBlur(img, (5, 5), 0)
			# imgHSV2 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			# cv2.imwrite("./imgHSV.jpg", imgHSV2)

			# We take just a group of lines from the image
			firstLine = (int)((1.0 - Params.params.view_height)*Params.params.size_y) - Params.params.ray_height_radius
			lastLine = firstLine + 2*Params.params.ray_height_radius
			imgReduced = img[firstLine:(lastLine + 1)]

			# cv2.imwrite("./imgReduced.jpg", imgReduced)

			# Blurring and converting to HSV values
			imgReduced = cv2.GaussianBlur(imgReduced, (5, 5), 0)
			imgHSV = cv2.cvtColor(imgReduced, cv2.COLOR_BGR2HSV)

			cv2.imwrite("./imgHSVReduced.jpg", imgHSV)

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
			cpt = 1
			for ray in imgRays :
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
					if nbDetect > ((Params.params.ray_width_radius + 1) * (Params.params.ray_height_radius + 1))/2 :
						if nbDetect > maxDetect :
							maxDetect = nbDetect
							listDetect[-1] = color


				countDetect.append(hashDetect)
				listMasks.append(hashMasks)

				cpt += 1
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