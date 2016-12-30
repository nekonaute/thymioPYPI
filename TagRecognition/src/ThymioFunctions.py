# -*- coding: utf-8 -*-
import dbus
import dbus.mainloop.glib
import gobject
import time
from optparse import OptionParser
import os
from constants import DEMO

AESL_PATH=os.path.join(os.path.dirname(__file__), 'asebaCommands.aesl')


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
leftSpeed = dbus.Array([0])
rightSpeed = dbus.Array([0])
proxSensors = [0, 0, 0, 0, 0, 0, 0]
acc = [0, 0, 0]
ambiant = [0,0]
reflected = [0,0]
delta = [0,0]
buttons = [0, 0, 0, 0, 0]
temperature = dbus.Array([0])


red=[32,1,0]
green=[5,32,0]
blue=[0,0,32]
yellow=[32, 32, 0]
turquoise=[0,32, 32]
pink=[32,1,5]
white=[32, 32, 32]
purple=[15, 0, 32]
orange=[32, 5, 0]
skyBlue=[5,32,25]

def dbusReply():
    pass

def dbusError(e):
    print 'error %s'
    print str(e)
 
def getVariablesError(e):
    print 'error : '
    print str(e)

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


def updateLeftSpeedValue(left):
    global leftSpeed
    leftSpeed = left

def updateRightSpeedValue(right):
    global rightSpeed
    rightSpeed = right

# Returns a list [leftWheelSpeed, rightWheelSpeed]
def getMotorSpeed():
	network.GetVariable("thymio-II", "motor.left.speed",reply_handler = updateLeftSpeedValue, error_handler = getVariablesError)
	actualLeftSpeed = int(leftSpeed[0])
	network.GetVariable("thymio-II", "motor.right.speed", reply_handler = updateRightSpeedValue, error_handler = getVariablesError)
	actualRightSpeed = int(rightSpeed[0])
	return [actualLeftSpeed, actualRightSpeed]

# Modify the speed of each wheel as asked
def setMotorSpeed(left, right):
	network.SetVariable("thymio-II", "motor.left.target", [left])
	network.SetVariable("thymio-II", "motor.right.target", [right])

# give thymio a direction
# thymio turns in one second
def turn(angle):
	actualLeftSpeed, actualRightSpeed = getMotorSpeed()
	angularSpeed=0#(angle*32.)/9
	if angle > 0:
		otherWheel = actualRightSpeed/4 
		setMotorSpeed(angularSpeed+actualLeftSpeed, otherWheel)#actualRightSpeed)
	else :
		otherWheel = actualLeftSpeed/4 
		setMotorSpeed(otherWheel,angularSpeed+actualRightSpeed) #actualLeftSpeed,angularSpeed+actualRightSpeed)
	#setMotorSpeed(actualLeftSpeed, actualRightSpeed)

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

# leds : 
# options are : 
# "red", "blue", "green", "turquoise", "yellow", 
# "pink", "white", "purple", "orange", "skyBlue"


def setLeds(color):
	#network.LoadScripts(AESL_PATH, reply_handler=updateLed, error_handler=getVariablesError)
	network.SendEventName("SetColor", color)#, reply_handler=updateLed, error_handler=getVariablesError)

def turnOffLeds():
	#network.LoadScripts(AESL_PATH, reply_handler=updateLed, error_handler=getVariablesError)
	network.SendEventName("SetColor", [0,0,0])#, reply_handler=updateLed, error_handler=getVariablesError)

def setSound(freq,dur):
	network.LoadScripts(AESL_PATH)#, reply_handler=updateLed, error_handler=getVariablesError)
	network.SendEventName("SetSound", [freq, dur])#, reply_handler=dbusReply, error_handler=dbusError)

def flash(color1, color2):
    setLeds(color1)
    setLeds(color1)
    turnOffLeds()
    turnOffLeds()
    setLeds(color2)
    setLeds(color2)
    turnOffLeds()


def updateLed():
	pass

parser = OptionParser()
parser.add_option("-s", "--system", action="store_true", dest="system", default=False,help="use the system bus instead of the session bus")
parser.add_option("-d", "--demo", action="store_true", dest="demo", default=False,help="activate the demo mode to see what robot sees")

(options, args) = parser.parse_args()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# setting the demo global attribute
DEMO = options.demo

if options.system:
    bus = dbus.SystemBus()
else:
    bus = dbus.SessionBus()

#Create Aseba network 
network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')
network.LoadScripts(AESL_PATH, reply_handler=dbusReply, error_handler=dbusError)
print "Connection OK"
