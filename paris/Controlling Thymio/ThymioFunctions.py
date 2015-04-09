import dbus
import dbus.mainloop.glib
import gobject
#import sys
import time
from optparse import OptionParser

# peripheral sensors
leftSensor = 0
frontLeftSensor = 1
frontSensor = 2
frontRightSensor = 3
rightSensor = 4
backLeftSensor = 5
backRightSensor = 6

# buttons on the thymio
backwardButton = 0
leftButton = 1
centerButton = 2
forwardButton = 3
rightButton = 4

# directions of the accelerometer
rightToLeft = 0
frontToBack = 1
topToBottom = 2

# variables to get from ASEBA variables (or to set)
speed = dbus.Array([0])
proxSensors = [0, 0, 0, 0, 0, 0, 0]
acc = [0, 0, 0]
ambiant = [0,0]
reflected = [0,0]
delta = [0,0]
buttons = [0, 0, 0, 0, 0]
temperature = dbus.Array([0])

def dbusReply():
    pass

def dbusError(e):
    print 'error %s'
    print str(e)
 
def getVariablesError(e):
    print 'error : '
    print str(e)
    loop.quit()


def updateSensorValue(r):
    global proxSensors
    proxSensors = r

# Returns the value of the sensorName sensor (0 if nothing, 4500 if smthng's close)
def getSensorValue(sensorName):
	network.GetVariable("thymio-II", "prox.horizontal", reply_handler = updateSensorValue, error_handler = getVariablesError)
	return proxSensors[sensorName]



# Ground sensors (3 arrays...)

def updateAmbiantValue(r):
    global ambiant
    ambiant = r

# Returns the value of the ground sensor in term of ambiant light intensity on the ground (0 = no light, 1023 = maximal light)
# ambiant[0] = value for the left sensor, ambiant[1] = value for the right sensor
def getAmbiantValue():
	network.GetVariable("thymio-II", "prox.ground.ambiant", reply_handler = updateAmbiantValue, error_handler = getVariablesError)
	return ambiant


def updateReflectedValue(r):
    global reflected
    reflected = r

# Returns the value of the ground sensor in term of quantity of received light when IR is emitted (0 = no reflection, 1023 = maximal reflection)
# reflected[0] = value for the left sensor, reflected[1] = value for the right sensor
def getReflectedValue():
	network.GetVariable("thymio-II", "prox.ground.reflected", reply_handler = updateReflectedValue, error_handler = getVariablesError)
	return reflected


def updateDeltaValue(r):
    global delta
    delta = r

# Returns the value of the ground sensor in term of difference between reflected light and ambiant light (linked with distance and color of the ground)
# delta[0] = value for the left sensor, delta[1] = value for the right sensor
def getDeltaValue():
	network.GetVariable("thymio-II", "prox.ground.delta", reply_handler = updateDeltaValue, error_handler = getVariablesError)
	return delta




def updateButtonValue(r):
    global buttons
    buttons = r

def getAllButtonValues():
	network.GetVariable("thymio-II", "buttons.binary", reply_handler = updateButtonValue, error_handler = getVariablesError)
	return buttons

# 0 or 1
def getButtonValue(buttonName):
	network.GetVariable("thymio-II", "buttons.binary", reply_handler = updateButtonValue, error_handler = getVariablesError)
	return buttons[buttonName]


def updateSpeedValue(r):
    global speed
    speed = r

# Returns a list [leftWheelSpeed, rightWheelSpeed]
def getMotorSpeed():
	network.GetVariable("thymio-II", "motor.left.speed",reply_handler = updateSpeedValue, error_handler = getVariablesError)
	actualLeftSpeed = int(speed[0])
	#print "type speed : ", type(actualLeftSpeed[0])
	#print "changing type : ", a, "its type : ", type(a)
	network.GetVariable("thymio-II", "motor.right.speed", reply_handler = updateSpeedValue, error_handler = getVariablesError)
	actualRightSpeed = int(speed[0])
	return [actualLeftSpeed, actualRightSpeed]

# Modify the speed of each wheel as asked
def setMotorSpeed(left, right):
	network.SetVariable("thymio-II", "motor.left.target", [left])
	network.SetVariable("thymio-II", "motor.right.target", [right])

#def setMotorSpeed2(translationalSpeed, rotationalSpeed):




def updateAccelerometerValue(r):
    global acc
    acc = r

def getAccelerometerValue(direction):
	network.GetVariable("thymio-II", "acc", reply_handler = updateAccelerometerValue, error_handler = getVariablesError)
	return acc[direction]



def updateTemperatureValue(r):
    global temperature
    temperature = r

# Returns the temperature in degrees Celsius
def getTemperatureValue():
	network.GetVariable("thymio-II", "temperature", reply_handler = updateTemperatureValue, error_handler = getVariablesError)
	return int(temperature[0])/10

