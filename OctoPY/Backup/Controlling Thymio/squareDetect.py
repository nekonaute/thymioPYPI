import numpy as np
import cv2
import imutils
import io
import picamera

import dbus
import dbus.mainloop.glib
import gobject
import time
from ThymioFunctions import *
from optparse import OptionParser

from movements import move
from tools import *

# the height of the resized image
taille=480.0

# initial speed
iniSpeedL = iniSpeedR = 50


# hue values : 
# red : 170-180 (even more like 178, 179)
# dark blue : 118
# sky blue : 100
# darkish green : 61-64
# normal green : 58
# green apple: 43



# image img is already resized !
def locateColorSquare(color, corner, camera):
	
	if time.time()-start > runTime:
		setMotorSpeed(0, 0)
		loop.quit()
	stream=io.BytesIO()

	# capture into stream
	camera.capture(stream, 'jpeg', use_video_port=True)
	data=np.fromstring(stream.getvalue(), dtype=np.uint8)
	img=cv2.imdecode(data, 1)

	img=imutils.resize(img, height=int(taille))

	#cv2.imshow("cameraImage", img)
	#cv2.waitKey(100)

	squares, positions = find_squares(img)
	for square, position in zip(squares, positions) :
		w, width, height=getContourImage(square, img)
		# if we have a possible square candidate
		if w.any():
			corn=getCorner(corner, w)

			his=Histogram(corn)
			hue=np.argmax(his)
			if color==1:
				# should be red
				if hue>170:
					print "correct color (red) detected ! Follow !"
					move3(taille, position, 10, 18)
					return True
				else : 
					continue
			if color == 2 :
				# should be blue
				if hue >= 85 and hue <=120 :
					print "correct color (blue) detected ! Follow"
					move3(taille, position, 10, 18)
					return True
				else:
					continue
			if color==3 :
				if hue >= 50 and hue <= 85 :
					print "correct color (green) detected ! Follow"
					move3(taille, position, 10, 18)
					return True
				else :
					continue
	# print "not detected"
	setLeds("orange")
	setMotorSpeed(iniSpeedL, iniSpeedR)	
	return True


if __name__ == '__main__':

    RED=1
    BLUE=2
    GREEN=3

    # SquareDetection Parameters
    color = RED
    corner=3

    # Image dimensions
    xTaille=640
    yTaille=480

    #runTime in seconds
    runTime=30
    start=time.time()
    #setMotorSpeed(iniSpeedL, iniSpeedR)
    with picamera.PiCamera() as camera:
	    camera.resolution=(xTaille, yTaille)
	    #print in the terminal the name of each Aseba NOde
	    print network.GetNodesList()
	    #GObject loop
	    print 'starting loop'
	    #setting Thymio's initial speed
	    setMotorSpeed(iniSpeedL, iniSpeedR)
	    loop = gobject.MainLoop()
	    #Running runTime seconds
	    handle = gobject.timeout_add (100, locateColorSquare, color, corner, camera) #every 0.1 sec
	    loop.run()
	    turnOffLeds()
	    setMotorSpeed(0,0)
   


