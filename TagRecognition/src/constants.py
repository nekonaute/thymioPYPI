# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 18:38:36 2016

@author: daphnehb
"""
from default_cst import *
from plot_constants import *
from path_constants import *
import numpy as np
import cv2

IEME_TAG = 0

#to test different parameters of Canny's algo
CANNY_VIDEO_MAKER={}

CANNY_PERCENTAGE = 1/2

THRESH_VALUE = lambda : 135 #2.04*INIT_BRIGHTNESS

# for the brightness evaluation
LAST_IMGS_MEAN = []
# the minimum and maximum values acceptable for brightness
BRIGHT_MEAN_MIN = 135
BRIGHT_MEAN_MAX = 155

# different convolution matrix
k_contraste = np.array([[0, 0, 0, 0, 0], [0, 0, -1, 0, 0], [0, -1, 5, -1, 0], [0, 0, -1, 0, 0], [0, 0, 0, 0, 0]])
k_bords = np.array([[0, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 1, -4, 1, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0]])
kernel_float32 = np.ones((5, 5), np.float32) / 25
kernel_uint8 = np.ones((5, 5), np.uint8)
kernel = np.ones((5,5),np.uint8)


# TEMPLATES SIZES
# size of the tag in pixel for different distances
# hardcode
HEIGHT20 = 350
WIDTH20 = 270
HEIGHT30 = 225
WIDTH30 = 175
HEIGHT40 = 170
WIDTH40 = 125
HEIGHT50 = 130
WIDTH50 = 100
HEIGHT65 = 95
WIDTH65 = 75
HEIGHT80 = 75
WIDTH80 = 55

# used min/max height/width
# distances in cm
DIST_MIN = 20
HEIGHT_MIN = HEIGHT20
WIDTH_MIN = WIDTH20
DIST_MAX = 80
HEIGHT_MAX = HEIGHT80
WIDTH_MAX = WIDTH80

def get_initial_shape():
    img = cv2.imread(TAG_TEMPLATE_INIT, 0)
    return img.shape

HEIGHT0,WIDTH0 = 296,225

# conversion cm->pixels
CM_PIX = 118.1