# -*- coding: utf-8 -*-
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import tools
import found_tag_box as td

DISTANCE = 20

def get_calibrations():
    global DISTANCE
	print "Distance de ",DISTANCE,"cm"
	# initialize the camera and grab a reference to the raw camera capture
	camera = PiCamera()
	camera.resolution = (tools.SIZE_X, tools.SIZE_Y)
	#camera.framerate = 64
	camera.brightness = tools.INIT_BRIGHTNESS

	rawCapture = PiRGBArray(camera, size=(tools.SIZE_X, tools.SIZE_Y))
	print "Initializing camera"
	# allow the camera to warmup
	time.sleep(3)
	camera.start_preview()
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array

		rawCapture.truncate(0)
		# not working : cv2 not showing
		# if the `q` key was pressed, break from the loop
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		contours = td.getTagBox_vEmilias(gray)
		if contours is None:
			continue
		for c in contours:
			i1 = image.copy()
			cv2.drawContours(i1,[c], -1,(255,0,0),1)
			cv2.imshow("Réalité",i1)
			key = cv2.waitKey(0) & 0xFF
			if key == ord('s'):
				cv2.imwrite(tools.get_template_path()+"tag_template"+str(DISTANCE)+".png",image)
				c = tools.order_corners(c)
				print c
				print "Taille tag (pixels) ", tools.shape_contour(c)
		print "Quit?"
		key = cv2.waitKey(0) & 0xFF
		if key == ord("q"):
			break
	cv2.destroyAllWindows()
	
def show_bot_reality():
	# initialize the camera and grab a reference to the raw camera capture
	camera = PiCamera()
	camera.resolution = (tools.SIZE_X, tools.SIZE_Y)
	#camera.framerate = 64
	camera.brightness = tools.INIT_BRIGHTNESS

	rawCapture = PiRGBArray(camera, size=(tools.SIZE_X, tools.SIZE_Y))
	print "Initializing camera"
	# allow the camera to warmup
	time.sleep(3)
	camera.start_preview()
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		cv2.imshow("reality",image)

		rawCapture.truncate(0)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
	cv2.destroyAllWindows()

show_bot_reality()
