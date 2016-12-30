# -*- coding: utf-8 -*-
from SimulationControlThymio import * # thread controlling the thymio
from launch_rasp import RaspbClass as Raspb
from optparse import OptionParser
import generePlots as plt


if __name__ == '__main__':
	runTime = 50
	# getting back args
	parser = OptionParser()
	parser.add_option("-d", "--demo", action="store_true", dest="demo", default=False,help="activate the demo mode to see what robot sees")
	(options, args) = parser.parse_args()
	DEMO = options.demo
	
	thymio_sim = SimulationControlThymio()
	raspberry = Raspb(thymio_sim)
#	raspberry.tag_expected([(256,"10"),(320,"10"),(0,"00")])
	raspberry.bot_expected([341,98,15])
	raspberry.set_demo(DEMO)
	try:
		print "Launching thymio"
		thymio_sim.start()
		print "Thymio in process"
		# the prog relies on the raspberry
		print 'starting loop'
		raspberry.start()
		print "Press Ctrl+c to stop"
	except KeyboardInterrupt:
		print "Ctrl+c -> Stopping"
		raspberry.stopping() # will also stop the thymio thread
		thymio_sim.join()
	finally:
		plt.plot_brightness_freq()
        plt.plot_brightness_evol()
        plt.results_pie_chart()
    

