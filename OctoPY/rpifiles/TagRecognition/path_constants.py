# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

@author : daphnehb & emilie
"""
import os

# constants
ABS_PATH_PRINC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG_PATH = ABS_PATH_PRINC + "/data/img/"
SHOOT_PATH = ABS_PATH_PRINC + "/data/shoots/"
PLOT_PATH = ABS_PATH_PRINC + "/data/plots/"
FILE_PATH = ABS_PATH_PRINC + "/data/files/"
LOG_PATH = ABS_PATH_PRINC + "/data/files/log/"
TESTS_PATH = ABS_PATH_PRINC + "/data/tests/"
VIDEO_PATH = ABS_PATH_PRINC + "/data/video/"
TEMPLATE_PATH = ABS_PATH_PRINC + "/data/templates/"
TAGS_PATH = ABS_PATH_PRINC + "/data/tags/"
CALIBR_PATH = ABS_PATH_PRINC + "/data/calibration/"

def get_template_path():
    size_dir = str(SIZE_X)+"_"+str(SIZE_Y)+"/"
    return CALIBR_PATH+size_dir

TAG_TEMPLATE_INIT = TEMPLATE_PATH+"tag_template_init.png"
