import io
import time
import picamera
from PIL import Image
import cv2
import numpy as np

# Image dimensions
xTaille=640
yTaille=480

lowerPink = np.array([166,50,50])
upperPink = np.array([174,255,255])

# lowerBound and upperBound designate the bounds for the color we want to find
# given in np.array of a triplet HSV (hue, saturation, value)
def locateColor(img, lowerBound, upperBound):
    image = cv2.GaussianBlur(img,(5,5),0)

    image_HSV = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(image_HSV, lowerBound, upperBound)
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
        # Compute the coordinates of the center of the largest contour
        coordinates = cv2.moments(contours[largest])
        targetX = int(coordinates['m10']/coordinates['m00'])
        targetY = int(coordinates['m01']/coordinates['m00'])
	print "coordinates of located object : ", targetX, targetY
	# The angle designating Thymio's direction : 
	# -90 : completely left
	#  90 : completely right
	#   0 : straight
	
	# insert fucntions to move thymio here

	angle=(float(targetX)/xTaille)*180 - 90
	if angle<0: 
	   print "angle =", angle, " : TURN LEFT"
	if angle > 0: 
	   print "angle =", angle, " : TURN RIGHT"
	if angle==0: 
	   print "angle =", angle, " : GO STRAIGHT" 
	
	"""
        # Pick a suitable diameter for our target (grows with the contour) and
        # draw on a target
	
	diam = int(np.sqrt(area)/4)
        cv2.circle(image,(targetX,targetY),diam,(0,255,0),1)
        cv2.line(image,(targetX-2*diam,targetY),(targetX+2*diam,targetY),(0,255,0),1)
        cv2.line(image,(targetX,targetY-2*diam),(targetX,targetY+2*diam),(0,255,0),1)
	cv2.imshow('View',image)
	cv2.waitKey(0)
	"""
    else:
	print "no object of specified color found!!!!"


def outputs():
    stream = io.BytesIO()
    # number of images to take
    for i in range(20):
        # This returns the stream for the camera to capture to
        yield stream
        # Once the capture is complete, the loop continues here
	data=np.fromstring(stream.getvalue(), dtype=np.uint8)
	img=cv2.imdecode(data, 1)
	#print img.shape
	locateColor(img, lowerPink, upperPink)
	#cv2.imshow('myimg', img)
	# Reset the stream for the next capture
        stream.seek(0)
        stream.truncate()

with picamera.PiCamera() as camera:
    camera.resolution = (xTaille, yTaille)
    camera.framerate = 80
    time.sleep(2)
    start = time.time()
    camera.capture_sequence(outputs(), 'jpeg', use_video_port=True)
    finish = time.time()
    print finish - start
    #print('Captured 40 images at %.2ffps' % (40 / (finish - start)))
