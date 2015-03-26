import dbus
import dbus.mainloop.glib
import gobject
#import sys
import time
from optparse import OptionParser

# peripheral sensors
left_sensor = 0
front_left_sensor = 1
front_sensor = 2
front_right_sensor = 3
right_sensor = 4
back_left_sensor = 5
back_right_sensor = 6

# buttons on the thymio
backward_button = 0
left_button = 1
center_button = 2
forward_button = 3
right_button = 4

# directions for accelerometer
right_to_left = 0
front_to_back = 1
top_to_bottom = 2

# GLOBAL VARIABLES
start=time.time()
run_time=10
speed=dbus.Array([0])
prox_sensors=[0, 0, 0, 0, 0, 0, 0]
acc=[0, 0, 0]
ambiant=[0,0]
reflected=[0,0]
delta=[0,0]
buttons=[0, 0, 0, 0, 0]
temperature=dbus.Array([0])

def dbusReply():
    pass

def dbusError(e):
    print 'error %s'
    print str(e)
 
def get_variables_error(e):
    print 'error : '
    print str(e)
    loop.quit()


def get_variables_reply_sensor_value(r):
    global prox_sensors
    prox_sensors = r

# Returns the value of the sensorName sensor (0 if nothing, 4500 if smthng's close)
def get_sensor_value(sensorName):
	network.GetVariable("thymio-II", "prox.horizontal", reply_handler = get_variables_reply_sensor_value, error_handler = get_variables_error)
	return prox_sensors[sensorName]



# Ground sensors (3 arrays...)

def get_variables_reply_ambiant_value(r):
    global ambiant
    ambiant = r

# Returns the value of the ground sensor in term of ambiant light intensity on the ground (0 = no light, 1023 = maximal light)
# ambiant[0] = value for the left sensor, ambiant[1] = value for the right sensor
def get_ambiant_value():
	network.GetVariable("thymio-II", "prox.ground.ambiant", reply_handler = get_variables_reply_ambiant_value, error_handler = get_variables_error)
	return ambiant


def get_variables_reply_reflected_value(r):
    global reflected
    reflected = r

# Returns the value of the ground sensor in term of quantity of received light when IR is emitted (0 = no reflection, 1023 = maximal reflection)
# reflected[0] = value for the left sensor, reflected[1] = value for the right sensor
def get_reflected_value():
	network.GetVariable("thymio-II", "prox.ground.reflected", reply_handler = get_variables_reply_reflected_value, error_handler = get_variables_error)
	return reflected


def get_variables_reply_delta_value(r):
    global delta
    delta = r

# Returns the value of the ground sensor in term of difference between reflected light and ambiant light (linked with distance and color of the ground)
# delta[0] = value for the left sensor, delta[1] = value for the right sensor
def get_delta_value():
	network.GetVariable("thymio-II", "prox.ground.delta", reply_handler = get_variables_reply_delta_value, error_handler = get_variables_error)
	return delta




def get_variables_reply_button_value(r):
    global buttons
    buttons = r

# 0 or 1
def get_button_value(buttonName):
	network.GetVariable("thymio-II", "buttons.binary", reply_handler = get_variables_reply_button_value, error_handler = get_variables_error)
	return buttons[buttonName]


def get_variables_reply_speed_value(r):
    global speed
    speed = r

# Returns a list [leftWheelSpeed, rightWheelSpeed]
def get_motor_speed():
	network.GetVariable("thymio-II", "motor.left.speed",reply_handler = get_variables_reply_speed_value, error_handler = get_variables_error)
	actual_left_speed = int(speed[0])
	#print "type speed : ", type(actual_left_speed[0])
	#print "changing type : ", a, "its type : ", type(a)
	network.GetVariable("thymio-II", "motor.right.speed", reply_handler = get_variables_reply_speed_value, error_handler = get_variables_error)
	actual_right_speed = int(speed[0])
	return [actual_left_speed, actual_right_speed]

# Modify the speed of each wheel as asked
def set_motor_speed(left, right):
	network.SetVariable("thymio-II", "motor.left.target", [left])
	network.SetVariable("thymio-II", "motor.right.target", [right])

#def setMotorSpeed2(translational_speed, rotational_speed):




def get_variables_reply_accelerometer_value(r):
    global acc
    acc = r

def get_accelerometer_value(direction):
	network.GetVariable("thymio-II", "acc", reply_handler = get_variables_reply_accelerometer_value, error_handler = get_variables_error)
	return acc[direction]



def get_variables_reply_temperature_value(r):
    global temperature
    temperature = r

# Returns the temperature in degrees Celsius
def get_temperature_value():
	network.GetVariable("thymio-II", "temperature", reply_handler = get_variables_reply_temperature_value, error_handler = get_variables_error)
	return int(temperature[0])/10

