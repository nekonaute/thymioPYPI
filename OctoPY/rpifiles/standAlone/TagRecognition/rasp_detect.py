# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

"""


# import the necessary packages
import numpy as np
import cv2,os
from picamera import PiCamera
from picamera.array import PiRGBArray
import time, datetime
# from our files
import tools
import found_tag_box as tg
import gestIO as io
import generePlots as plt

def initCam():
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (tools.SIZE_X, tools.SIZE_Y)
    #camera.framerate = 64
    camera.brightness = tools.INIT_BRIGHTNESS
    rawCapture = PiRGBArray(camera, size=(tools.SIZE_X, tools.SIZE_Y))
    # allow the camera to warmup
    time.sleep(3)
    return camera, rawCapture

def test_brightness(save=False):
    """
    save : To save the images of any change
    plot: To plot the apparition frequency of each brightness
    & To plot the evolution of the brightness according to time
    """
    i = 0
    i_save = 0
    saving=0
    camera, rawCapture = initCam()
    d_dur = time.time()
    print "Default bright =",camera.brightness
    #camera.brightness = 0
    #print "Initial test brightness = 0"
    print "Starting video"
    #camera.start_preview()
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        # Capture frame-by-frame
        print "\nBrightness",i," : ",camera.brightness," (pixel mean =",image.mean(),")"
        i += 1
        cv2.imshow("img", image)
        dt = time.time()
        if i%tools.BRIGHTNESS_CHECK!=0:
            verif = tools.verify_brightness(image)
        else:
            verif = tools.verify_brightness(image,go=True)
        print "Checking time :",time.time()-dt
        # there were a modification
        if verif!=0:
            camera.brightness += verif
            # if the option save is ok
            saving = 2 if save else 0 # activating the saving of the 2 images
            i_save = i
        # saving the current image
        if saving!=0:
            cv2.imshow("saved",image)
            cv2.imwrite(tools.IMG_PATH+"img"+str(i_save)+"_"+str(saving)+"_toB"+str(camera.brightness)+".png", image)
            saving -= 1
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        #camera.brightness += 10
        time.sleep(tools.WAITING_TIME)
        # if the `q` key was pressed, break from the loop
        if key == ord("q") :
            tools.BRIGHT_PLOT_TIME = time.time()-d_dur
            break
    # end with
    print "\nFin prise"
    # When everything done, release the capture
    # camera.stop_preview()
    cv2.destroyAllWindows()
    plt.plot_brightness_freq()
    plt.plot_brightness_evol()

def take_images(directory):
    i = 0
    camera, rawCapture = initCam()
    print "Starting video"
    #camera.start_preview()
    directory = tools.IMG_PATH+directory
    if not os.path.exists(directory):
        os.makedirs(directory)
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        # Capture frame-by-frame
        i += 1
        cv2.imshow("img", image)
        cv2.imwrite(str(directory)+"tag_view"+str(i)+".png",image)
        time.sleep(tools.WAITING_TIME)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        # if the `q` key was pressed, break from the loop
        if key == ord("q") or i >= tools.ITERATIONS:
            break
    # end with
    print "\nFin prise"
    # When everything done, release the capture
    # camera.stop_preview()
    cv2.destroyAllWindows()


def test_images(classification,directory):
    ststr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%Hh%Mmin%Ssec')
    string="\n Prises du {} \n".format(ststr)
    string+="***Calculs des true/false-positives/negatives***"
    print "\nDébut tests"
    nbImgSec = 0
    st = time.time()
    #accepted = [(3,"10"),(12,"10"),(10,"00"),(0,"00")]
    list_img = sorted(os.listdir(tools.IMG_PATH+str(directory)))
    for i,img_name in enumerate(list_img):
        img = cv2.imread(tools.IMG_PATH+str(directory)+img_name)
        nbImgSec += 1
        string += "\n--------> Prise n°{}".format(i)
        dt = time.time()
        # showing what's found
        results = tg.found_tag_img(img,demo=True)
        ft = time.time()
        tps = "\nTemps = " + str(ft - dt)
        if results == []:
            tps += " ---> No tag found"
        else:
            tps += " ---> Tags found:" + str(results)
        #print "Résultats image",i," = ", results
        cv2.imshow("image",img)
        string += str(tps)
        solution = classification[img_name]
        # categorizing
        if results==[] and solution==[]:
            tools.TRUE_NEG+=1
        elif results==[]:
            tools.FALSE_NEG+=1
        elif solution==[]:
            tools.FALSE_POS+=1
        else:
            resIn = all([x in solution for x in results])
            solIn = all([x in results for x in solution])
            if solIn and resIn:
            # it is a good good one
                tools.TRUE_POS+=1
            elif solIn :
                tools.FALSE_NEG+=1
            elif resIn :
                tools.FALSE_POS+=1
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break
        if (dt - st >= 1):
            print "\n\t1 seconde écoulée : {} images testées".format(nbImgSec)
            string += "\n\t1 seconde écoulée : {} images testées".format(nbImgSec)
            st = time.time()
            nbImgSec = 0

    cv2.destroyAllWindows()
    io.writeOutputFile(string)
    plt.results_equi_pie_chart()
    print "\nFin tests"


def takeVideo(demo=False,comparison=False,save=False):
    i = 0
    nbImgSec = 0
    tag = None
    st = dt = time.time()
    camera, rawCapture = initCam()
    ststr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%Hh%Mmin%Ssec')
    string="\n Prises du {} sur {} itérations\n".format(ststr,tools.ITERATIONS)
    string += "\n***Récupération des données de l'arène***"
    string += "\n\tInitial brightness = {}".format(camera.brightness)
    string += "\n\tCamera asked framerate = {}".format(camera.framerate)
    string += "\n\tCamera resolution = {}".format(camera.resolution)
    log_writer = io.WriteLog(string)
    log_writer.start()
    print "Starting video"
    # camera.start_preview()
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        try:
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
            image = frame.array
            nbImgSec += 1
            i += 1
            string = "\n--------> Prise n°{}".format(i)
            print "\ntemps ++", time.time()-dt
            dt = time.time()
            if i%tools.BRIGHTNESS_CHECK!=0:
                verif = tools.verify_brightness(image)
            else:
                verif = tools.verify_brightness(image,go=True)
            # there were a modification
            if verif!=0:
                camera.brightness += verif
            print "tps bright",time.time()-dt
            # tests sur l'image
            results = []
            if comparison:
                tps = tg.found_tag_img_comps(image)
            else:
                results = tg.found_tag_img(image, demo=demo, save=save)
            tps = "\nTemps = "+str(time.time() - dt)
            # writing if there was or not any tag in the image
            if results==[]:
                tps+= " ---> No tag found"
            else:
                tps += " ---> Tags found:"+str(results)
                print "Résultats = ",results
            string += str(tps)
            if tag is None:
                # continue
                tag = image
            ft = time.time()
            print 'Temps mis = {}'.format(ft-dt)
            # show the frame
            key = cv2.waitKey(1) & 0xFF

            rawCapture.truncate(0)
            dt = time.time()
            # to save the image
            if (dt - st >= 1):
                print "\n\t1 seconde écoulée : {} images prises".format(nbImgSec)
                string += "\n\t1 seconde écoulée : {} images prises".format(nbImgSec)
                st = ft
                nbImgSec = 0
            log_writer.nextString(string)
            # if the `q` key was pressed, break from the loop
            if key == ord("q") :#or i>=tools.ITERATIONS:
                break
        except KeyboardInterrupt:
            # Ctrl+C
            break
        #except Exception as e:
        #    log_writer.nextString("\nException Raised"+str(type(e))+":"+str(e)+"\n")

    # end for
    print "\nFin prise"
    log_writer.stopping()
    # When everything's done, release the capture
    #camera.stop_preview()
    cv2.destroyAllWindows()
    if comparison:
        io.writeOutputFile(string)
        plt.plotBestTime()
        plt.boxPlotBestTime()
    log_writer.join()
