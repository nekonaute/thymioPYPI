# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 18:38:36 2016

@author: daphnehb
"""

DEMO = False
SAVING = True

# iterations (images to take)
ITERATIONS = 50
WAITING_TIME = 1

# resolution of the image
SIZE_X = 640 #720  # 2592
SIZE_Y = 480 #576  # 1944

# setting initial brightness and brightness step for a change
BRIGHTNESS_STEP = 5
INIT_BRIGHTNESS = 60
# number of images for brightness comparison
BRIGHTNESS_COMP = 5
BRIGHT_MIN_WRONG_IMG = 2 # nb >=1
# checking and checking brightness every 
BRIGHTNESS_CHECK = 15

# tag definition
# in pixel
SUPP_MARGIN = 3
# in cm
OCCLUSION_MARGIN = 1
TAG_HEIGHT = 10.4
TAG_WIDTH = 7.8
NB_LIGN_CASE = 3
NB_COL_CASE = 3
