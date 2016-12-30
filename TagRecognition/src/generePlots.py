# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 14:53:58 2016

@author: daphnehb & emilie
"""
import tools
import numpy as np
import matplotlib.pyplot as plt

def boxPlotBestTime():
    """
    Getting the box plots with outsider
    Testing with our ex-filters, elias's and improved elias's
    """
    if tools.TPS_ELIAS==[] or tools.TPS_EMILIAS==[] or tools.TPS_NOUS==[]:
        print "Boxplots comparing algorithms not generated"
        return None
    plt.figure()
    plt.boxplot([tools.TPS_NOUS,tools.TPS_ELIAS,tools.TPS_EMILIAS])
    plt.xticks([1,2,3],["Our","Elias","Emilias"])
    plt.ylabel("Times (seconds)")
    plt.title("Comparison of filters used (boxplots")
    plt.savefig(tools.PLOT_PATH+'diff_filters_box.png')
    print "Boxplots comparing algorithms saved"
    plt.show()

def plotBestTime():
    """
    Getting the curve plots with outsider
    Testing with our ex-filters, elias's and improved elias's
    """
    if tools.TPS_ELIAS==[] or tools.TPS_EMILIAS==[] or tools.TPS_NOUS==[]:
        print "Curve plots comparing algorithms not generated"
        return None
    plt.figure()
    plt.plot(tools.TPS_NOUS)
    plt.plot(tools.TPS_ELIAS)
    plt.plot(tools.TPS_EMILIAS)
    plt.title("Comparison of filters used (plots)")
    plt.xticks([])
    plt.xlabel("")
    plt.ylabel("Times (seconds)")
    plt.legend(["Our","Elias","Emilias"], loc='upper left')
    plt.savefig(tools.PLOT_PATH+'diff_filters_curves.png')
    print "Curve plots comparing algorithms saved"
    plt.show()

def boxPlotBestThresh():
    """
    Getting the box plots with outsider
    Testing with our ex-filters, elias's and improved elias's
    """
    if tools.TPS_FIX==[] or tools.TPS_CALC==[] or tools.TPS_OTSU==[]:
        print "Boxplots comparing thresholds not generated"
        return None
    plt.figure()
    plt.boxplot([tools.TPS_FIX,tools.TPS_CALC,tools.TPS_OTSU],0,"")
    plt.xticks([1,2,3],["Fixed","2.04*brightness","Otsu"])
    plt.ylabel("Times (seconds)")
    plt.title("Comparison of thresholds used (boxplots")
    plt.savefig(tools.PLOT_PATH+'diff_thresh_box.png')
    print "Boxplots comparing thresholds saved"
    plt.show()

def plotBestThresh():
    """
    Getting the curve plots with outsider
    Testing with our ex-filters, elias's and improved elias's
    """
    if tools.TPS_FIX==[] or tools.TPS_CALC==[] or tools.TPS_OTSU==[]:
        print "Curve plots comparing thresholds not generated"
        return None
    plt.figure()
    plt.plot(tools.TPS_FIX)
    plt.plot(tools.TPS_CALC)
    plt.plot(tools.TPS_OTSU)
    plt.title("Comparison of thresholds used (plots)")
    plt.xticks([])
    plt.xlabel("")
    plt.ylabel("Times (seconds)")
    plt.legend(["Fixed","2.04*brightness","Otsu"], loc='upper left')
    plt.savefig(tools.PLOT_PATH+'diff_thresh_curves.png')
    print "Curve plots comparing thresholds saved"
    #plt.show()

def results_equi_pie_chart():
    if tools.TRUE_NEG==0 and tools.TRUE_POS==0 and tools.FALSE_NEG==0 and tools.FALSE_POS==0:
        print "Pie chart of results not generated"
        return None
    plt.figure()
    # The slices will be ordered and plotted counter-clockwise.
    labels = 'True positives', 'True negatives', 'False positives', 'False negatives'
    sizes = [tools.TRUE_POS, tools.TRUE_NEG, tools.FALSE_POS, tools.FALSE_NEG]
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.savefig(tools.PLOT_PATH+"results_percentages_classified.png")
    print "Pie chart of results saved"
    #plt.show()

def results_pie_chart():
    if tools.TRUE_POS==0 and tools.FALSE_POS==0:
        print "Pie chart of results not generated"
        return None
    plt.figure()
    # The slices will be ordered and plotted counter-clockwise.
    labels = 'True positives', 'False positives'
    sizes = [tools.TRUE_POS,tools.FALSE_POS]
    colors = ['gold', 'lightskyblue']
    explode = (0, 0.1)  # only "explode" the 2nd slice
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.savefig(tools.PLOT_PATH+"results_percentages_auto.png")
    print "Pie chart of results saved"
    #plt.show()
    
def real_percentages_pie(classification):
    true_pos = true_neg = 0
    for val in classification.values():
        if val==[]:
            true_neg +=1
        else:
            true_pos += 1
    plt.figure()
    labels = 'True positives', 'True negatives'
    sizes = [true_pos,true_neg]
    #colors = ['yellowgreen', 'lightskyblue']
    explode = (0, 0.1)  # only "explode" the 2nd slice

    plt.pie(sizes, explode=explode, labels=labels,
        autopct='%1.1f%%', shadow=True)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.savefig(tools.PLOT_PATH+"expected_percentages.png")
    print "Pie chart of classification saved"
    #plt.show()

def plot_brightness_freq():
    if tools.BRIGHT_PLOT==[]:
        print "Frequency brightness not generated"
        return None
    plt.figure()
    plt.hist(tools.BRIGHT_PLOT)
    plt.title("Frequency for each possible brightness")
    plt.xticks(np.arange(0,105,5))
    plt.xlabel("Brightness")
    plt.ylabel("Frequency (for each image brightness change)")
    plt.savefig(tools.PLOT_PATH+'brightness_freq.png')
    print "Frequency brightness saved"
    #plt.show()
    
def plot_brightness_evol():
    if tools.BRIGHT_PLOT==[]:
        print "Evolution brightness not generated"
        return None
    plt.figure()
    bright_diff = np.arange(0,105,5)
    bright_len = len(tools.BRIGHT_PLOT)
    time_tab = np.linspace(0,tools.BRIGHT_PLOT_TIME,bright_len)
    time_tab_cut = [time_tab[0],time_tab[bright_len-1]]
    plt.plot(tools.BRIGHT_PLOT)
    plt.title("Evolution of the brightness")
    plt.xlabel("Times (seconds)")
    plt.xticks(time_tab_cut)
    plt.yticks(bright_diff)
    plt.ylabel("Brightness")
    plt.savefig(tools.PLOT_PATH+'brightness_evol.png')
    print "Evolution of the brightness saved"
    #plt.show()
