import dbus
import dbus.mainloop.glib
import gobject
#import sys
import time
from ThymioFunctions import *
from optparse import OptionParser

def stop():
    setMotorSpeed(0, 0)
    loop.quit()


if __name__ == '__main__':
    print network.GetNodesList()
    #GObject loop
    print 'starting loop'
    loop = gobject.MainLoop()
    handle = gobject.timeout_add (100, stop) #every 0.1 sec
    loop.run()


