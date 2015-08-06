import time
import random
import picamera
import io

import Params
import Simulation

class SimulationDetectColor(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__camera = picamera.PiCamera()
		self.__camera.resolution = (Params.params.size_x, Params.params.size_y)

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		try :
			stream = io.BytesIO()

			# Capture into stream
			self.__camera.capture(stream, 'jpeg', use_video_port = True)
			data = np.fromstring(stream.getvalue(), dtype = np.uint8)
			img = cv2.imdecode(data, 1)

			# Blurring and converting to HSV values
			image = cv2.GaussianBlur(img, (5, 5), 0)
			image_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

			# Locate the color
			mask = cv2.inRange(image_HSV, np.array([100, 50, 50]), np.array([110, 255, 255]))
			mask = cv2.GaussianBlur(mask, (5, 5), 0)

			# We get a list of the outlines of the white shapes in the mask
			contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

			# If we have at least one contour, we look through each one and pick the biggest
			if len(contours) > 0 :
				largest = 0
				area = 0

				for i in range(len(contours)) :
					# Get the area of the ith contour
					temp_area = cv2.contourArea(contours[i])

					# If it is the biggest we have seen, keep it
					if temp_area > area :
						area = temp_area
						largest = i

				# Compute the coordinates of the center of the largest contour
				coordinates = cv2.moments(contours[largest])
				targetX = int(coordinates['m10']/coordinates['m00'])
				targetY = int(coordinates['m01']/coordinates['m00'])

				angle = (float(targetX), Params.params.size_x) * 66 - 33
				minSize = 900
				maxSize = 30000
				self.move2(angle, area, minSize, maxSize, 100, 100)
			else :
				self.tController.setMotorSpeed(0, 0)

			self.waitForControllerResponse()
			time.sleep(0.1)
		except :
			self.mainLogger.critical('SimulationDetectColor - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())

