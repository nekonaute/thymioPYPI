import dbus
import dbus.mainloop.glib
import gobject
import time
from ThymioFunctions import *
from optparse import OptionParser

def avoidingObstacles():

    for i in xrange(7):
        proxSensors[i]=getSensorValue(i)
	
   #Parameters of the Braitenberg, to give weight to each wheels 
    leftWheel=[0.01,0.05,-0.07,-0.05,-0.01, 0.03, 0.04]
    rightWheel=[-0.01,-0.05,-0.07,0.05,0.01,0.04, 0.03]

    #Braitenberg algorithm
    totalLeft=0
    totalRight=0
    for i in range(7):
        totalLeft=totalLeft+(proxSensors[i]*leftWheel[i])
        totalRight=totalRight+(proxSensors[i]*rightWheel[i])

    # add a constant speed to each wheels so the robot moves always forward
    totalRight=totalRight+100
    totalLeft=totalLeft+100

    # send motor value to the robot 
    setMotorSpeed(totalLeft, totalRight)
    if time.time()-start>=runTime:
        setMotorSpeed(0, 0)
        print time.time()-start
        loop.quit()
        return False

    return True


if __name__ == '__main__':

    start = time.time()
    runTime = 10
    #print in the terminal the name of each Aseba NOde
    print network.GetNodesList()
 
    #GObject loop
    print 'starting loop'
    loop = gobject.MainLoop()
    #call the callback of Braitenberg algorithm
    handle = gobject.timeout_add (100, avoidingObstacles) #every 0.1 sec
    loop.run()

