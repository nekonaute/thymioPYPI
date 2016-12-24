# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

@author : daphnehb & emilie
"""

import rasp_detect as td
import generePlots as plt
import classification as cl
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-c", "--compare", action="store_true", dest="compare", default=False,help="to start comparing the three possible algo")
parser.add_option("-d", "--demo", action="store_true", dest="demo", default=False,help="activate the demo mode to see what robot sees")
parser.add_option("-b", "--bright", action="store_true", dest="brightest", default=False,help="launching the brightness test")
parser.add_option("-s", "--save", action="store_true", dest="save", default=False,help="activating the saving of the images taken")
parser.add_option("-l", "--classification", action="store_true", dest="classing", default=False,help="test the algorithm with images already classified")
parser.add_option("-k", "--take_classification", action="store_true", dest="take_classing", default=False,help="take images for next time classification")

(options, args) = parser.parse_args()

demo = options.demo
comparison = options.compare

""" Testing the robot's launch """

# to test the brightness changing following the luminosity of the room
if options.brightest:
    td.test_brightness(save=options.save)
    exit()

if options.classing:
    td.test_images(cl.accepted,cl.directory)
    #plt.real_percentages_pie(cl.accepted)
    exit()

if options.take_classing:
    # to take images to test them with classification
    td.take_images(cl.directory)
    exit()

#if not options.anormal and not options.classing and not options.take_classing and not options.brightest:
    # to test the video programm
td.takeVideo(demo=demo,comparison=comparison,save=options.save)
exit()

""" Trying to re-generate and save the plot corresponding to what was tested """
# Done in each called function
#plt.plotBestTime()
#plt.boxPlotBestTime()
#plt.results_pie_chart()
#plt.plot_brightness_freq()
#plt.plot_brightness_evol()
