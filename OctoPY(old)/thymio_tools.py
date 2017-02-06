from ThymioFunctions import *
from math import pi
import time
import random

speed = 50
angle_max = 100


def go_forward():
    setMotorSpeed(speed,speed)
    
def go_backward():
    setMotorSpeed(-speed,-speed)
    
def turn_left(angle):
    # computation to do with time
    time.sleep(angle*0.01)
    turn(angle)
    
def turn_right(angle):
    # computation to do with time
    time.sleep(angle*0.01)
    turn(-angle)
    
def make_noise():
    pass

def stop():
    setMotorSpeed(0,0)
    
def random_walk():
    while True:
        # not working
        # if the user want to stop the robot
        butt_center = getButtonValue(centerButton)
        if butt_center:
            stop()
            break
            
        # random action launched
        action = random.randint(0, 5)
        print "action =",action
	# Go forward
	if action == 0 :
	    go_forward()
	# Turn Left
	elif action == 1 :
	    turn_left(random.randint(0,angle_max))
	# Turn Right
	elif action == 2 :
	    turn_right(random.randint(0,angle_max))
	# Go backward
	elif action == 3 :
	    go_backward()
	# Stop
	elif action == 4 :
	    stop()
	    break
	# Sound
	elif action == 5 :
	    pass
	print getAllButtonValues()
	# waiting
	sleepTime = random.random()
	time.sleep(sleepTime)


for c in [red,yellow,green,turquoise,purple,white,skyBlue,pink,orange]:
    setLeds(c)
    time.sleep(1)

#random_walk()