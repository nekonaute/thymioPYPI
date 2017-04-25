import numpy as np
import cv2

def draw_contours(image,contours):
    cv2.drawContours(image, contours, -1, (0,255,0), 3)
    return image

def show_image(image,window='image',last=True):
    cv2.imshow(window,image)
    cv2.waitKey(0)
    if last:
        cv2.destroyAllWindows()

def read_image(path):
    """
    load as UNIT8 image
    """
    return cv2.imread(path)

def threshold(image,t):
    """
    for CV_8U image aka np.uint8
    """
    ret,thresh = cv2.threshold(image,t,255,0)
    return thresh

def resize_image(image,fx=0.25,fy=0.25,interpolation=cv2.INTER_LINEAR):
    return cv2.resize(image,None,fx=fx,fy=fy,interpolation=interpolation)

def convert_grey(image):
    """
    0 to 255 for CV_8U images aka  np.uint8, usually raspberry camera frames
    0 to 65535 for CV_16U images aka  np.uint16
    0 to 1 for CV_32F images aka  np.float32
    """
    gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return gray_image
