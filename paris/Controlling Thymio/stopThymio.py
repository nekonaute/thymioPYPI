import dbus
import dbus.mainloop.glib
import gobject
import time
from ThymioFunctions import *
from optparse import OptionParser


# leds : 
# options are : 
# "red", "blue", "green", "turquoise", "yellow", 
# "pink", "white", "purple", "orange", "skyBlue"


def stop():
    turnOffLeds()
    setMotorSpeed(0,0)
    loop.quit()


if __name__ == '__main__':

    print network.GetNodesList()
    #GObject loop
    print 'starting loop'
    loop = gobject.MainLoop()
    #call the callback of Braitenberg algorithm
    handle = gobject.timeout_add (50, stop) #every 0.1 sec
    loop.run()


