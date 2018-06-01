import numpy as np
import cv2

def high_contrast(image):
    mx,mn = np.max(image),np.min(image)
    image = (image - mn)/float(mx-mn)
    image = image**2
    image = (image)*255
    return np.array((image),dtype=np.uint8)
				
def convert_to_HSV(image):
    """
        convert image to HSV color space
    """
    hsv_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    return hsv_image

def draw_contours(image,contours):
    cv2.drawContours(image, contours, -1, (0,255,0), 3)
    return image

def threshold_range(image,lower, upper):
    thresholded = cv2.inRange(image, lower, upper)
    return thresholded

def findContours(image,structure_type,approx_method):
    """                     
        Organize found contours
    """
    im, contours, hierarchy = cv2.findContours(image,structure_type,approx_method)
    return contours, hierarchy

def masked_image(image,mask_image):
    """ Bitwise-AND mask and original image """
    res = cv2.bitwise_and(image,image, mask= mask_image)

def show_image(image,window='image',still=True,fps=25.):
    cv2.imshow(window,image)
    cv2.waitKey(0) # wait untill key
    cv2.destroyAllWindows()
    #cv2.waitKey(int((1/fps)*1000)) # in ms

def automatic_canny(gray_image):
    """
        Use Canny edge detction algorythm
    """
    y,x = gray_image.shape
    win_frac = 3
    l_image = gray_image[y/win_frac:y-(y/win_frac),(x/win_frac):x/(win_frac-1)-((x/win_frac))]
    r_image = gray_image[y/win_frac:y-(y/win_frac),x/(win_frac-1)-(x/win_frac):x-(x/win_frac)]
    v = (np.mean(l_image) + np.mean(r_image))/2.
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edge_image = cv2.Canny(gray_image, lower, upper)
    return edge_image

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

def resize_image(image,fx=0.5,fy=0.5,interpolation=cv2.INTER_NEAREST):
    return cv2.resize(image,None,fx=fx,fy=fy,interpolation=interpolation)

def convert_grey(image):
    """
    0 to 255 for CV_8U images aka  np.uint8, usually raspberry camera frames
    0 to 65535 for CV_16U images aka  np.uint16
    0 to 1 for CV_32F images aka  np.float32
    """
    gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return gray_image
