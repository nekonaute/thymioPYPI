# classes.py created on March 12, 2015. Jacqueline Heinerman & Massimiliano Rango

# import python libraries?
import parameters as pr

# define global variables
global NB_DIST_SENS		# number of proximity sensors
global TIME_STEP  		# time step of the simulation in seconds
global NMBRWEIGHTS 		# number of weigths in the NN = (7*2)+ 2 = 16
global MAXSPEED         # maximum motor speed
global SENSOR_MAX       # max sensor value

NB_DIST_SENS = 7
NMBRWEIGHTS = 16
MAXSPEED = 500
SENSOR_MAX = 4500 # XXX: found sensor with max value of 5100
TIME_STEP = 0.05 # = 50 milliseconds. IMPORTANT: keep updated with TIME_STEP constant in asebaCommands.aesl

class Candidate(object):
    def __init__(self, memome,fitness,sigma,genome):
        self.memome = memome
        self.fitness = fitness
        self.sigma = sigma
        self.genome = genome

class RobotMemomeDataMessage(object):
    def __init__(self, destination,fitness,memome):
        self.destionation = destination
        self.fitness = fitness
        self.memome = memome

class RobotGenomeDataMessage(object):
    def __init__(self, destination,fitness,genome):
        self.destionation = destination
        self.fitness = fitness
        self.genome = genome