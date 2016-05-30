import io
import time
import picamera
from PIL import Image
import cv2
import numpy as np


import dbus
import dbus.mainloop.glib
import gobject
from optparse import OptionParser

from movements import move2, move

iniSpeedL = iniSpeedR = 100

def detectColor(camera, lowerBound, upperBoud, xTaille, runTime):

		if time.time()-start > runTime:
			setMotorSpeed(0, 0)
			loop.quit()
		
		stream=io.BytesIO()
	
		# capture into stream
		camera.capture(stream, 'jpeg', use_video_port=True)
		data=np.fromstring(stream.getvalue(), dtype=np.uint8)
		img=cv2.imdecode(data, 1)
	
		# blurruing and converting to HSV values	
		image = cv2.GaussianBlur(img,(5,5),0)
		image_HSV = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
	
		# locate the color
  	mask = cv2.inRange(image_HSV, lowerBound, upperBoud)
  	mask = cv2.GaussianBlur(mask,(5,5),0)

	 	# findContours returns a list of the outlines of the white shapes in the mask
	 	contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		# If we have at least one contour, look through each one and pick the biggest
    if len(contours)>0:
						largest = 0
		      	area = 0
		      	for i in range(len(contours)):
		          		# get the area of the ith contour
		          		temp_area = cv2.contourArea(contours[i])
		          		# if it is the biggest we have seen, keep it
		          		if temp_area > area:
		              		area = temp_area
		              		largest = i
						# print "object found!"
						# Compute the coordinates of the center of the largest contour
		      	coordinates = cv2.moments(contours[largest])
		      	targetX = int(coordinates['m10']/coordinates['m00'])
		      	targetY = int(coordinates['m01']/coordinates['m00'])
						#print "coordinates of located object : ", targetX, targetY
						# The angle designating Thymio's direction : 
						# -90 : completely left
						#  90 : completely right
						#   0 : straight
						
						# insert functions to move thymio here
		
						angle=(float(targetX)/xTaille)*66 - 33
						minSize = 900
						maxSize = 30000
						move2(angle, area, minSize, maxSize, iniSpeedL, iniSpeedR)
		
						# Pick a suitable diameter for our target (grows with the contour) and
						# draw on a targetxTaille
						"""
						diam = int(np.sqrt(area)/4)
									cv2.circle(image,(targetX,targetY),diam,(0,255,0),1)
									cv2.line(image,(targetX-2*diam,targetY),(targetX+2*diam,targetY),(0,255,0),1)
									cv2.line(image,(targetX,targetY-2*diam),(targetX,targetY+2*diam),(0,255,0),1)
						cv2.imshow('View',image)
						cv2.waitKey(100)
						"""
						return True
    else:
						setMotorSpeed(0,0)
						print "no object of specified color found"
						return True
	

if __name__ == '__main__':

    # Image dimensions
    xTaille=320
    yTaille=240
    lowerPink = np.array([150,50,50])
    upperPink = np.array([180,255,255])
    #lowerBlue = np.array([100,50,50])
    #upperBlue = np.array([110,255,255])
    #runTime in seconds
    runTime=30
    start=time.time()

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
	    handle = gobject.timeout_add (100, detectColor, camera, lowerPink, upperPink, xTaille, runTime) #every 0.1 sec
	    
	    loop.run()
    setMotorSpeed(0,0)
