from VanillaEE.SimulationVanillaEE import *

"""

main = SimulationVanillaEE (None,None)

print network.GetNodesList()
start = time.time()
runTime = 100
#print in the terminal the name of each Aseba NOde
print "begin !!"
while main.avoidingObstacles():#main.step() :
    pass
    
"""   

if __name__ == '__main__':

    start = time.time()
    runTime = 10
    #print in the terminal the name of each Aseba NOde
    print network.GetNodesList()
    main = SimulationVanillaEE (None,None)
    #GObject loop
    print 'starting loop'
    #loop = gobject.MainLoop()
    #call the callback of Braitenberg algorithm
    handle = gobject.timeout_add (10, main.step) #every 0.1 sec
    loop.run()
  