import numpy as np

import dbus
import dbus.mainloop.glib
import gobject
from ThymioFunctions import *
from optparse import OptionParser


# turns tymio without any movement
def turn(angle):
	actualLeftSpeed, actualRightSpeed = getMotorSpeed()
	print "current speed", actualLeftSpeed, actualRightSpeed
	angularSpeed=(angle*32.)/9
	
	if angle < 1 and angle > -1 :
		m=np.max([actualLeftSpeed, actualRightSpeed])
		setMotorSpeed(m, m)
	if angle > 0:
		setMotorSpeed(angularSpeed+actualLeftSpeed, actualRightSpeed-angularSpeed)
		print "thymio's moving right"
	else :
		angularSpeed=angularSpeed*-1
		setMotorSpeed(actualLeftSpeed-angularSpeed, angularSpeed+actualRightSpeed)
		print "thymio's moving left"


# if area is greater than 3000, the object is right in front of us
# if area is less than 1000, the object is too far
def move(angle, iniSpeedL, iniSpeedR):
	setMotorSpeed(iniSpeedL,iniSpeedR)
	angularSpeed=(angle*32.)/9
	setLeds("green")
	if angle < 1 and angle > -1 :
		setMotorSpeed(iniSpeedL, iniSpeedR)
		return
	if angle > 0:
		setMotorSpeed(angularSpeed+iniSpeedL, iniSpeedR-angularSpeed)
		return
	else:
		angularSpeed=angularSpeed*-1
		setMotorSpeed(iniSpeedL-angularSpeed, angularSpeed+iniSpeedR)


# if area is greater than maxSize, the object is right in front of us
# if area is less than minSize, the object is too far
# minSize=900, maxSize=30000 works fine
def move2(angle, area, minSize, maxSize, iniSpeedL, iniSpeedR):
	if area>maxSize:
		print "object is right in front of us !"
		setMotorSpeed(0,0)
		return
	if area<minSize:
		print "object is too far"
		setMotorSpeed(0,0)
		return
	move(angle, iniSpeedL, iniSpeedR)



# function to move/turn thymio left or right. Thymio goes straight if 
# he the center is in epsilon's reach of imageWidth/2
# speed = 18 works fine when iniSpeedL=iniSpeedR=100 (speed to turn)
def move3(imageWidth, center, epsilon, speed):
	actualLeftSpeed, actualRightSpeed = getMotorSpeed()
	setLeds("green")
	if center[0]<(imageWidth/2.0) - epsilon:
		print "TURN LEFT"
		# thymio moves left
		setMotorSpeed(actualLeftSpeed-speed, actualRightSpeed+speed)
		return True
	if center[0]>(imageWidth/2.0) + epsilon:
		print "TURN RIGHT"
		setMotorSpeed(actualLeftSpeed+speed, actualRightSpeed-speed)
		# thymio moves right
		return True
	setMotorSpeed(iniSpeedL, iniSpeedR)
	print "THYMIO GOES STRAIGHT"
	return True




