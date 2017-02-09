# -*- coding: utf-8 -*-

"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Gestion de la PiCamera pour en faire un capteur de lumière.
"""

# import the necessary packages
import numpy as np
#import cv2,os
import picamera as pc
import time

def initCam():
    # initialize the camera and grab a reference to the raw camera capture
    camera = pc.PiCamera()
    camera.resolution = (100, 100)
    camera.brightness = 60
    
    time.sleep(3)
    return camera
    
def lightCaptor(camera):
    
    image = np.empty((128,112,3),dtype=np.uint8)
    camera.capture(image, 'rgb')
    image = image[:100,:100]
    return image.mean()
    
