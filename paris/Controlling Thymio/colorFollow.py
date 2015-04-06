import io
import time
import picamera
from PIL import Image
import cv2
import numpy as np
import dbus
import dbus.mainloop.glib
import gobject
#import sys
import time
from ThymioFunctions import *
from optparse import OptionParser


# Image dimensions
xTaille=320
yTaille=240

# some thresholds for colors in HSV format
lowerPink = np.array([166,50,50])
upperPink = np.array([174,255,255])
lowerBlue = np.array([90,50,50])
upperBlue = np.array([105,255,255])



# turns Thymio toward object situated at angle degrees
# angle is between -90 and 90, where -90 is completely to the left of Thymio and 
# 90 completely to the right 
def turn(angle):
	actualLeftSpeed, actualRightSpeed = getMotorSpeed()
	angularSpeed=(angle*35.)/9
	#print "OLD SPEED : ", actualLeftSpeed, actualRightSpeed
	if angle < 1 and angle > -1 :
		#print "don't move"		
		return
	setMotorSpeed(angularSpeed+actualLeftSpeed,actualRightSpeed-angularSpeed)
	"""	
	# object is located to the right
	if angle > 0:
		setMotorSpeed(angularSpeed+actualLeftSpeed,actualRightSpeed-angularSpeed)
		#print "NEW SPEED :", angularSpeed+actualLeftSpeed,actualRightSpeed-angularSpeed
	else :
		angularSpeed=angularSpeed*-1
		setMotorSpeed(actualLeftSpeed-angularSpeed,angularSpeed+actualRightSpeed)
		#print "NEW SPEED :", actualLeftSpeed,angularSpeed+actualRightSpeed
	"""


def detectColor(camera, lowerBound, upperBoud):
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

	# If we have at least one contour, look through each one and pick the biggest object
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
			#print "size of largest area : ", area
			if area < 500 : 
				print "Object too far"
				return  

			# Compute the coordinates of the center of the largest contour
        	coordinates = cv2.moments(contours[largest])
        	targetX = int(coordinates['m10']/coordinates['m00'])
        	targetY = int(coordinates['m01']/coordinates['m00'])

			# The angle designating Thymio's direction : 
			# -90 : completely left
			#  90 : completely right
			#   0 : straight
	
			# raspberry pi's camera is between -33 and 33 degrees
			angle=(float(targetX)/xTaille)*33*2 - 33
		
			# turn Thymio toward this object
			turn(angle)
			"""
			if angle<0: 
		   		print "angle =", angle, " : TURN LEFT"
			if angle > 0: 
		  		print "angle =", angle, " : TURN RIGHT"
			if angle==0: 
		   		print "angle =", angle, " : GO STRAIGHT" 
		
			"""
	
        
	        # TO SHOW THE TARGETTED REGION : 

	        """
	        # Pick a suitable diameter for our target (grows with the contour) and
	        # draw on a targetxTaille
			
			diam = int(np.sqrt(area)/4)
	        cv2.circle(image,(targetX,targetY),diam,(0,255,0),1)
	        cv2.line(image,(targetX-2*diam,targetY),(targetX+2*diam,targetY),(0,255,0),1)
	        cv2.line(image,(targetX,targetY-2*diam),(targetX,targetY+2*diam),(0,255,0),1)
			cv2.imshow('View',image)
			cv2.waitKey(3)
			"""
		
    	else:
			print "no object of specified color found!!!!"
			setMotorSpeed(0,0)

with picamera.PiCamera() as camera:
	camera.resolution=(xTaille, yTaille)
	# nbPhotos : amount of photos to take 
	nbPhotos=100
	for i in xrange(nbPhotos):
		detectColor(camera, lowerBlue, upperBlue)



if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", "--system", action="store_true", dest="system", default=False,help="use the system bus instead of the session bus")
 
    (options, args) = parser.parse_args()
 
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
 
    if options.system:
        bus = dbus.SystemBus()
    else:
        bus = dbus.SessionBus()
 
    #Create Aseba network 
    network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')
 
    setMotorSpeed(0,0)

