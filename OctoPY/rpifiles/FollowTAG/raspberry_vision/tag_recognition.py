import cv2
import numpy as np
from numpy import linalg as lnag

TRIANGLE_TYPE = 0
SQUARE_TYPE = 1

def pre_processing_image(image):
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return imgray

def countour_extreme_points(contour):
    extLeft,extRight,extTop,extBottom = None,None,None,None
    extLeft = np.array(contour[contour[:, :, 0].argmin()][0])
    extRight = np.array(contour[contour[:, :, 0].argmax()][0])
    extTop = np.array(contour[contour[:, :, 1].argmin()][0])
    extBottom = np.array(contour[contour[:, :, 1].argmax()][0])
    return extLeft,extRight,extTop,extBottom

def triangle_orientation(L,R,T,B):
    """
        0: left
        1: right
    """
    collisions = np.array([lnag.norm(T-R),lnag.norm(B-R),lnag.norm(T-L),lnag.norm(B-L)])
    collision = np.argmin(collisions)
    if collision == 0 or collision == 1:
        return 0
    else:
        return 1

def countours_extreme_points(contours):
    extsLeft,extsRight,extsTop,extsBottom = [],[],[],[]
    for c in contours:
        extLeft,extRight,extTop,extBottom = countour_extreme_points(c)
        extsLeft += [ extLeft ]
        extsRight += [ extRight ]
        extsTop += [ extTop ]
        extsBottom += [ extBottom ]
    return extsLeft,extsRight,extsTop,extsBottom
    
def resize_image(img,fx=0.25,fy=0.25,interpolation=cv2.INTER_LINEAR):
	return cv2.resize(img,None,fx=fx,fy=fy,interpolation=interpolation)
	
def get_scene_grey_centroids(image,k=3):
	"""
		usually on resized image
	"""
	z = np.float32(image.reshape((-1,1)))
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)
	ret,labels,centers=cv2.kmeans(z,k,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
	return centers
	
def search_tag(imgray, ar, sigma=1.0, eps=100):
    """
        eps and sigma are found experimentally
        post ptocessing
    """
    contours, hierarchy = cv2.findContours(imgray,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    tag_ids = []
    if hierarchy == None:
        return contours, tag_ids
    hierarchy = hierarchy[0]
    n = len(contours)
    tag_contours = []
    check = np.zeros(n)
    for curr in xrange(1,n):
        child = hierarchy[curr][2]
        if child!=-1:
            area_1 = cv2.contourArea(contours[curr])
            area_2 = cv2.contourArea(contours[child])
            if area_2!=0:
                area_ratio = area_1/area_2
                if area_ratio <= ar+2*sigma and area_ratio >= ar-2*sigma and area_1>eps:
                	if check[curr] == 0:
                		check[curr] = 1
                		tag_contours+= [contours[curr]]
                	if check[child] == 0:
                		check[child] = 1
                		tag_contours+= [contours[child]]
    return tag_contours, []


def detecting_tag(imgray, ar, sigma=1.0, eps=100):
    """
        eps and sigma are found experimentally
        post processing
    """
    resized_image=resize_image(imgray)
    centers = get_scene_grey_centroids(resized_image)
    tag_contours = []
    for center in centers:
    	ret,thresh = cv2.threshold(imgray,np.uint8(center),255,0)
    	contours, = search_tag(thresh,ar,sigma=sigma,eps=eps)
    	tag_contours += contours
    return tag_contours,[]
    

def estimate_Affine(src,dst, tag_type=TRIANGLE_TYPE):
    if tag_type == TRIANGLE_TYPE:
        src = add_center_triangle(src_tag_edges)
        dst = add_center_triangle(dst_tag_edges)
    estimated_M = cv2.getPerspectiveTransform(src, dst)
    return estimated_M

def add_center_triangle(t):
    ox = (t[0][0]+t[1][0]+t[2][0])/3.
    oy = (t[0][1]+t[1][1]+t[2][1])/3.
    return np.vstack((t,[ox,oy]))
