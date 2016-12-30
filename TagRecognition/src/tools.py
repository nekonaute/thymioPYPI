# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 19:21:36 2016

@author: daphnehb & emilief
"""

import time
import find_tag_id as tagid
from math import sqrt, fabs
# to make files more legible
from constants import *


def check_change_brightness(list_means):
    global BRIGHTNESS_MIN, BRIGHTNESS_MAX, BRIGHTNESS_COMP, BRIGHTNESS_STEP, INIT_BRIGHTNESS
    BRIGHT_PLOT.append(INIT_BRIGHTNESS)
    print "Checking brightness with mean images :",list_means
    tab_min = [x<BRIGHT_MEAN_MIN for x in list_means]
    where_min = tab_min.count(True)
    # if there are too many images under the thresh intervalle
    change = 0
    if where_min>=BRIGHT_MIN_WRONG_IMG:
        change = BRIGHTNESS_STEP
        print "Increasing the brightness of the camera: +{}".format(change)
    else:
        tab_max = [x>BRIGHT_MEAN_MAX for x in list_means]
        where_max = tab_max.count(True)
        # if there are too many images over the thresh intervallle
        if where_max>=BRIGHT_MIN_WRONG_IMG:
            change = -BRIGHTNESS_STEP
	    print "Reducing the brightness of the camera : {}".format(change)
    # re-setting the brightness
    INIT_BRIGHTNESS += change
    return change

def verify_brightness(image, go=False):
    global LAST_IMGS_MEAN, BRIGHTNESS_COMP
    n_mean = cv2.mean(image)[0]
    # more accurate but slower : n_mean = image.mean()
    if len(LAST_IMGS_MEAN)==BRIGHTNESS_COMP:
        LAST_IMGS_MEAN.pop(0)
        LAST_IMGS_MEAN.append(n_mean)
    else:
        LAST_IMGS_MEAN.append(n_mean)
    # if we do apply the verification
    change = 0
    if go:
    	change = check_change_brightness(LAST_IMGS_MEAN)
    return change

def color_gray_img(img, to_gray=True):
    if to_gray:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


"""
Black-White threshold
"""
def thresholding(img, seuil=THRESH_VALUE(), reverse=False, with_otsu=False, adaptative=False):
    if reverse:
        val = cv2.THRESH_BINARY_INV
    else:
        val = cv2.THRESH_BINARY
    if with_otsu:
        val += cv2.THRESH_OTSU
    if adaptative:
        _, thresh = cv2.adaptativeThreshold(img, seuil, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, val, 45, 0)
    else:
        _, thresh = cv2.threshold(img, seuil, 255, val)
    return thresh


def gradientSobelXY(img):
    gradX = cv2.Sobel(img, ddepth=cv2.cv.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(img, ddepth=cv2.cv.CV_32F, dx=0, dy=1, ksize=-1)
    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)
    return gradient

def isPerimeterOK(peri):
    peri_min = HEIGHT_MIN*2+WIDTH_MIN*2
    peri_max = HEIGHT_MAX*2+WIDTH_MAX*2
    if peri > peri_min or peri < peri_max:
        return False
    return True

def isAreaOK(area):
    area_min = HEIGHT_MIN*WIDTH_MIN
    area_max = HEIGHT_MAX*WIDTH_MAX
    if area > area_min or area < area_max:
        return False
    return True


def rectify(h):
    # order the box by top_left,top_right,bottom_right,bottom_left
    h = h.reshape((4, 2))
    hnew = np.zeros((4, 2), dtype=np.float32)

    add = h.sum(1)
    hnew[0] = h[np.argmin(add)]
    hnew[2] = h[np.argmax(add)]

    diff = np.diff(h, axis=1)
    hnew[1] = h[np.argmin(diff)]
    hnew[3] = h[np.argmax(diff)]
    return hnew

def order_corners(cnt):
    rect = cv2.minAreaRect(cnt)
    box = np.int0(cv2.cv.BoxPoints(rect))

    box = rectify(box)
    return box

def imgHomot(gray, cnt):
    box = order_corners(cnt)
    # getting the tag shape in pixel depending on its corners
    new_h, new_w = shape_contour(box) #(449,449)
    h = np.array([[0, 0], [new_w-1, 0], [new_w-1,new_h-1], [0, new_h-1]], np.float32)
    retval = cv2.getPerspectiveTransform(box, h)
    warp = cv2.warpPerspective(gray, retval, (new_w,new_h))
    return warp


def canny_algorithm(img):
    """
    img : img matrix
    """

    # Blur
    img = cv2.GaussianBlur(img, (3, 3), 0)
    # Canny edge detection using the computed median
    sigma = .10
    v = np.median(img)
    lower_thresh_val = int(max(0, (1.0 - sigma) * v))
    high_thresh_val = int(min(255, (1.0 + sigma) * v))
    img = cv2.Canny(img, lower_thresh_val, high_thresh_val)
    return img

def canny_lecture(image):
    # Blur
    at = time.time()
    img = cv2.GaussianBlur(image, (3, 3), 0)
    # high, low = 0.5*high
    dt = time.time()
    high_thresh_val, thresh_im = cv2.threshold(img, THRESH_VALUE(), 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    lower_thresh_val = 0.25 * high_thresh_val
    canny = cv2.Canny(img, lower_thresh_val, high_thresh_val)
    # end
    return canny


def canny_algorithm_v2(image):
    """
    img : img matrix
    """

    # Blur
    img = cv2.GaussianBlur(image, (3, 3), 0)
	# Canny edge detection using the computed median
    high_thresh_val, thresh_im = cv2.threshold(img, THRESH_VALUE(), 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lower_thresh_val = CANNY_PERCENTAGE * high_thresh_val
    img = cv2.Canny(img, lower_thresh_val, high_thresh_val)
    # end
    return img


def our_canny_algorithm(img):
    # find regions of the image that have high horizontal gradients and low vertical gradients
    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction
    gray = cv2.equalizeHist(img)
    (_, gr1) = cv2.threshold(gray, THRESH_VALUE(), 255, cv2.THRESH_BINARY_INV)# + cv2.THRESH_OTSU)
    ### apply Sobel gradient
    gradX = cv2.Sobel(gr1, ddepth=cv2.cv.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(gr1, ddepth=cv2.cv.CV_32F, dx=0, dy=1, ksize=-1)
    # subtract the y-gradient from the x-gradient
    gradient1 = cv2.subtract(gradX, gradY)
    gradient1 = cv2.convertScaleAbs(gradient1)
    return gradient1

def check_tags(image,gray, tagz_cont,demo=False,save=False):
	"""
	Foreach tag's contours found in the image, checking if it's a good one
	Return the list of tuples with (robot's number, robot's orientation string, robot's orientation angle, robot's distance, robot's direction from me)
	"""
	global IEME_TAG
	views = list()
	redz = list()
	greenz = list()
	# foreach contour found
	for cnt in tagz_cont:
		# take the contour and compute its bounding box
		# computing the min area bounding/fitting rect (even rotated)
		# getting the translation of the tag
		tag = imgHomot(gray, cnt)
		# check the id, orientation and coordinates of the bot
		# reading the info in the tag
		data =  tagid.lecture_tag(gray, tag, cnt)
		print "DATA =",data
		if data is None:
			# wrong tags in red
			redz.append(cnt)
			continue
		# tag found in green
		greenz.append(cnt)
		# adding them to the list views
		views.append(data)

	if demo or save:  # tag found in green
		cv2.drawContours(image, greenz, -1, (0, 255, 0), 2)
		cv2.drawContours(image, redz, -1, (0, 0, 255), 2)
		if save:
			cv2.imwrite(SHOOT_PATH+"image_"+str(IEME_TAG)+".png",image)
			IEME_TAG+=1
		if demo:
			cv2.imshow('Found',image)        
	return views

def verify_hierarchy(hierarchy, i):
    son = hierarchy[i, 2]
    if son==-1:
        return False
    enough_sons = 0
    for nc,c in enumerate(hierarchy):
        if nc==i: continue
        # if the hierarchy got i a a parent
        if c[3]==i:
            enough_sons+=1
    return (enough_sons>=4)

def euclidian_dist(min_c,max_c):
    coord_min = min_c
    coord_max = max_c
    left = (coord_min[0]-coord_max[0])*(coord_min[0]-coord_max[0])
    right = (coord_min[1]-coord_max[1])*(coord_min[1]-coord_max[1])
    return sqrt(left+right)

def isTriRect(side1,side2,hypothenusis):
    hyp2 = (hypothenusis*hypothenusis)
    side_sum = (side1 * side1) + (side2 * side2)
    if  fabs(hyp2-side_sum)<1000 :
        return True
    return False

def verify_measures(approx):
    approx = rectify(approx)  # getting top left,top right, bottom left, bottom right
    height, width = shape_contour(approx)
    if height<=width:
        return False
    # else
    ratio = width/float(height)
    # height/width must be in [0.70;0.80] if the tag is in the front
    diagonal = euclidian_dist(approx[0],approx[2])  # euclidian distance
    tri_rect = isTriRect(width, height, diagonal)
    if tri_rect and ratio>=0.60 and ratio<=0.80 :
            return True
    elif not tri_rect and ratio >= 0.30 and ratio <= 0.60:
        return True
    return False

def apply_filters(img):
    # Faster without np
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    cdf = hist.cumsum()
    cdf_m = np.ma.masked_equal(cdf, 0) #mask value equal to 0
    cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min())
    cdf = np.ma.filled(cdf_m, 0).astype('uint8')
    img3 = cdf[img]
    tt = time.time()
    ct = time.time()
    ret, thresh = cv2.threshold(img3, THRESH_VALUE(), 255, cv2.THRESH_BINARY)
    gt = time.time()
    ft = time.time()
    return thresh

def shape_contour(contour):
    """
    Only for contour with specific format top left,top right, bottom
    """
    width = max(contour[1][0]-contour[0][0], contour[3][0]-contour[2][0])
    height = max(contour[3][1]-contour[0][1],contour[2][1]-contour[1][1])
    return height,width
	
def tag_angle(tag_cont):
	height2= tag_cont[3,0,1] - tag_cont[0,0,1]
	height1= tag_cont[2,0,1] - tag_cont[1,0,1]
	diff = height1-height2  
	if fabs(diff) < 3:
		return 0.0
	else :
		ratio = height1/float(height2)
		if ratio<1 :
			return  (1-ratio) * 90
		else :
			return 90 * ratio	
	
def robot_angle(tag_contour,tag_orientation):
	if tag_orientation is None:
		return None
	tag_ang = tag_angle(tag_contour)
	if tag_orientation == "11":
		return (360 + tag_ang) % 360
	elif tag_orientation == "10" :
		return (90 + tag_ang) % 360
	elif tag_orientation == "00" :
		return (180 + tag_ang) % 360
	elif tag_orientation == "01" :
		return (270 + tag_ang) % 360
	else :
		return None
	
def verifChild(hierarchy, contour,peri_dad,area_dad):
    peri = cv2.arcLength(contour, True) # aproximation accuracy
    approx = cv2.approxPolyDP(contour, 0.04*peri, True)
    if len(approx)!=4 or not cv2.isContourConvex(approx):
        # not what we are searching for
        return 0,None
    # veifying the height and width
    approx = order_corners(approx) # getting top left,top right, bottom left, bottom right
    height, width = shape_contour(approx)
    #peri = (height+width)*2
    area = height*width
    peri_per = 100*float(peri)/peri_dad
    area_per = 100*float(area)/area_dad
    # the perimeter must be ~50% and area ~23% to be the direction child
    if peri_per<=60 and peri_per>=35 and area_per<=35 and area_per>=10:
        return 2,approx
    # the perimeter must be ~70% and area ~50% to be the id child
    if peri_per<=85 and peri_per>=55 and area_per<=70 and area_per>=35:
        return 1,approx
    # otherwise : not an interessant child
    return 0,None

def cont_in_cont(cont1,cont2):
    """
    Verify that cont2 isn't in cont1 or cont1 in cont2
    They have to not be close
    """
    # distance between
    x1,y1,w1,h1 = cv2.boundingRect(cont1)
    x2,y2,w2,h2 = cv2.boundingRect(cont2)
    dist1 = euclidian_dist([x1,y1],[x2,y2])
    dist2 = euclidian_dist([x1+w1,y1],[x2+w2,y2])
    dist3 = euclidian_dist([x1+w1,y1+h1],[x2+w2,y2+h2])
    dist4 = euclidian_dist([x1,y1+h1],[x2,y2+h2])
    if dist1<=5 or dist2<=5 or dist3<=5 or dist4<=5:
        return True
    return False


def contour_out_the_list(contour,list_cont):
    """
    Verify that the contour contour isn't included into another interesting contour
    """
    for c in list_cont:
        if cont_in_cont(c,contour):
            return False
    return True

def switch_side_img(img_side_val):
    img_side = round(img_side_val)
    if img_side == 0:
        return "inFront"
    elif img_side>0:
        return "atLeft"
    else:
        return "atRight"
