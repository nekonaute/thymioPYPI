import numpy as np
import cv2
import imutils
import time
import io
import picamera

import dbus
import dbus.mainloop.glib
import gobject
from ThymioFunctions import *
from optparse import OptionParser

from tools import *

# the height of the resized image
taille=240.0

# initial speed
iniSpeedL = iniSpeedR = 100


# hue values : 
# red : 170-180 (even more like 178, 179)
# dark blue : 118
# sky blue : 100
# darkish green : 61-64
# normal green : 58
# green apple: 43



# image img is already resized !
def communicate(qrcodes, camera):
	# stop if runtime has passed
	if time.time()-start > runTime:
		setMotorSpeed(0, 0)
		loop.quit()
	stream=io.BytesIO()

	# capture into stream
	camera.capture(stream, 'jpeg', use_video_port=True)
	data=np.fromstring(stream.getvalue(), dtype=np.uint8)
	img=cv2.imdecode(data, 1)

	img=imutils.resize(img, height=int(taille))

	# cv2.imshow("CameraImage", img)
	# cv2.waitKey(100)

	squares, positions = find_squares(img)
	for square, position in zip(squares, positions) :
		w, width, height=getContourImage(square, img)
		# if we have a possible square candidate
		if w.any():
			recognize=False
			for qrcode in qrcodes :
				color=qrcode[0]
				corner=qrcode[1]
				# to show the current square
				#cv2.imshow("SquareCandidate", w)
				#cv2.waitKey(100)
				corn=getCorner(corner, w)
				# display corner of square
				#cv2.imshow("corner", corn)
				#cv2.waitKey(100)
				his=Histogram(corn)
				hue=np.argmax(his)
				if color==1 :
					# red
					if hue>170 :
						print "Red detected in", corner, " Continue moving...."
						recognize=True
						break
					else :
						# seen thymio does not match this ID, continue detection
						continue

				if color==2 :
					# blue
					if hue >= 80 and hue <=120 : 
						print "Blue detected in", corner, " Continue moving...."
						recognize=True
						break
					else :
						# seen thymio does not match this ID, continue detection
						continue

				if color==3 : 
					# green
					if hue >= 40 and hue <=75 : 
						print "Green detected in", corner, "Continue moving...."
						recognize=True
						break
					else :
						# seen thymio does not match this ID, continue detection
						continue

			if not recognize :
				" I FOUND AN UNRECOGNIZED THYMIO! "
				# Thymio found an unrecognized ID 
				# stops to test if the other one is not moving
				setMotorSpeed(0,0)
				if isImmobile(width, height, camera, 10):
					print "IT'S NOT MOVING....LIGHTING UP!!"
					setLeds("pink")
					# stops for other thymio to see him
					time.sleep(3)
					setLeds("white")
					setMotorSpeed(iniSpeedL, iniSpeedR)
					return True

	print "NOT DETECTED"
	setLeds("white")
	actualLeftSpeed, actualRightSpeed = getMotorSpeed()
	# if thymio is already immobile then he moves again
	if actualLeftSpeed<3 and actualRightSpeed<3 :
		setMotorSpeed(iniSpeedL, iniSpeedR)
	return True


def isImmobile(width, height, camera, nbTests):

	if nbTests==0:
		# thymio immobile
		return True
	# the accepted error for movement
	epsilon=10

	if time.time()-start > runTime:
		setMotorSpeed(0, 0)
		loop.quit()
	stream=io.BytesIO()

	# capture into stream
	camera.capture(stream, 'jpeg', use_video_port=True)
	data=np.fromstring(stream.getvalue(), dtype=np.uint8)
	img=cv2.imdecode(data, 1)

	img=imutils.resize(img, height=int(taille))
	squares, positions = find_squares(img)

	for square, position in zip(squares, positions) :
		w, testWidth, testHeight=getContourImage(square, img)
		if w.any():
			if np.abs(testWidth-width)<= epsilon and np.abs(testHeight-height)<=epsilon :
				return isImmobile(width, height, camera, nbTests-1)
			else :
				continue
	# If we have went through all the squares and haven't found any the same size as before
	# then the image is not immobile
	return False



if __name__ == '__main__':

    RED=1
    BLUE=2
    GREEN=3

    # SquareDetection Parameters
    color1 = GREEN
    corner1=3

    color2= BLUE
    corner=2

    qrcode=[color1, corner1]
    qrcode2=[color2, corner]
    qrcodes=[qrcode, qrcode2]


    xTaille=320
    yTaille=240


    #runTime in seconds
    runTime=100
    start=time.time()
    setLeds("white")
    setMotorSpeed(iniSpeedL, iniSpeedR)

    with picamera.PiCamera() as camera:
	    camera.resolution=(xTaille, yTaille)
	    #print in the terminal the name of each Aseba NOde
	    print network.GetNodesList()
	    #GObject loop
	    print 'starting loop'
	    #setting Thymio's initial speed
	    #setMotorSpeed(100, 100)
	    loop = gobject.MainLoop()
	    #Running runTime seconds
	    handle = gobject.timeout_add (100, communicate, qrcodes, camera) #every 0.1 sec
	    loop.run()
	    turnOffLeds()
	    setMotorSpeed(0,0)


