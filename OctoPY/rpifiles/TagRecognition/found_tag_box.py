# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 15:28:36 2016

@author: 3200234
"""
import cv2
import time, tools

"""
Getting the initial gray image
Returning the simple tag found in this initial image
"""
def found_tag_img(img, demo=False,save=False):
    #try:
    # getting the corresponding tag box in complex image
    # getting the image in gray
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    contours = getTagBox_vEmilias(gray)
    result = []
    if demo:
        # to see every contours found equivalently : 
        view_demo(img,contours,demo)
    if contours:
        dt = time.time()
        # getting a simple image of the tag (only)
        # checking the tag
        robots_view = tools.check_tags(img,gray,contours,demo=demo,save=save)
        #print "Temps lecture :",time.time()-dt
        #print robots_view
        result = robots_view
    # else: nothing was found in the image
    #except: pass
    return result

def view_demo(img,contours,demo):
	img2 = img.copy()
	if contours : # contours found in blue
		cv2.drawContours(img2, contours, -1, (255, 0, 0), 4)
	if demo:
		cv2.imshow("Initial image",img2)

"""
Getting the initial gray image
Compare different algorithms (our,elias's and elias's remastered)
Returning the simple tag found in this initial image
"""
def found_tag_img_comps(img):
    # getting the corresponding tag box in complex image
    # getting the image in gray
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    string = ""
    ####### Our
    dt = time.time()
    contours = getTagBox_vOur(gray)
    # on ferme toutes les autres fenetres et on affiche juste le tag trouvé
    # enregistrement des img filtrees
    # getting a simple image of the tag (only)
    ft = time.time()
    if not contours is None:
        gray1 = img.copy()
        cv2.drawContours(gray1, contours, -1, (0, 0, 255), 4)
        cv2.imshow("before filter our",gray1)
    tools.TPS_NOUS.append(ft-dt)
    string+="\nTemps à Nous === {}".format(ft-dt)
    ####### Elias
    dt = time.time()
    contours = getTagBox_vElias(gray)
    # on ferme toutes les autres fenetres et on affiche juste le tag trouvé
    # enregistrement des img filtrees
    # getting a simple image of the tag (only)
    ft = time.time()
    if not contours is None:
        gray2 = img.copy()
        cv2.drawContours(gray2, contours, -1, (0, 255, 0), 4)
        cv2.imshow("before filter elias",gray2)
    tools.TPS_ELIAS.append(ft-dt)
    string+="\nTemps à Elias === {}".format(ft-dt)
    ####### Emilias
    dt = time.time()
    contours = getTagBox_vEmilias(gray)
    # on ferme toutes les autres fenetres et on affiche juste le tag trouvé
    # enregistrement des img filtrees
    # getting a simple image of the tag (only)
    ft = time.time()
    if not contours is None:
        gray3 = img.copy()
        cv2.drawContours(gray3, contours, -1, (255, 0, 0), 4)
        cv2.imshow("before filter emilias",gray3)
    tools.TPS_EMILIAS.append(ft-dt)
    string+="\nTemps à Emilias === {}".format(ft-dt)
    return string
    #tag_gray = tools.imgHomot(gray,box)
    #cv2.imshow('truc0',tag_gray)
    # reading the info in the tag
    #lecture_tag(tag_gray)
    #return tag_gray
    

# Grosse marge blanche pour que ca fonctionne "parfaitement"
def getTagBox_vOur(gray):
    
    edges3 = tools.our_canny_algorithm(gray).copy()
    (contours3,hierarchie3) = cv2.findContours(edges3, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    
    ### printing on the original image with all contours found
    #gray3 = img.copy()
    #cv2.drawContours(gray3, contours3, -1, (0, 0, 255), 4)
    #cv2.imshow("before filter ourlias",gray3)
    contours = contours3
    hierarchie = hierarchie3
    # if no contours were found, return None
    if len(contours) == 0:
    	return None
    # otherwise, sort the contours by area and compute the rotated
    # the contours with the largest area appear at the front of the list
    # bounding box of the largest contour
    cont = list()
    # for each contour, computing an approximation of this same contour as a polyedre
    for i,cnt in enumerate(contours):
        # approximate the contour
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        # if the shape got convex edges
        # & filter contour by 4angles shape
        if not cv2.isContourConvex(approx) or len(approx)!=4:
            continue
        # if that not a parallelogramm...
        # TODO 
        # if the length is between [10cm;50cm] the original shape
        # TODO
        # if a 30 cm ie taille(pixels)€[100*160;120;170]
        if not tools.isPerimeterOK(cv2.arcLength(approx,True)) :#or not isAreaOK(cv2.contourArea(approx)):
            continue
        # filter contour by almost one child
        # no parent?
        if hierarchie[0,i,2]!=-1 and hierarchie[0,i,3]==-1:
            cont.append(approx)
    # ATTENTION : making the assumption that the contour with the largest area is the barcoded region of the frame
    # the largest among those with exactly 4 corners and children
    if cont==[]:
	#cv2.imshow("no result",img)
        return None
    # printing the original image with all contours which passed filters
    #cv2.imshow("after filter",gray2)
    return cont

# Grosse marge blanche pour que ca fonctionne "parfaitement"
def getTagBox_vElias(gray):    
    edges3 = tools.canny_algorithm(gray).copy()
    (contours3,hierarchie3) = cv2.findContours(edges3, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    
    ### printing on the original image with all contours found
    #gray3 = img.copy()
    #cv2.drawContours(gray3, contours3, -1, (0, 0, 255), 4)
    #cv2.imshow("before filter ourlias",gray3)
    contours = contours3
    hierarchie = hierarchie3
    # if no contours were found, return None
    if len(contours) == 0:
    	return None
    # otherwise, sort the contours by area and compute the rotated
    # the contours with the largest area appear at the front of the list
    # bounding box of the largest contour
    cont = list()
    # for each contour, computing an approximation of this same contour as a polyedre
    for i,cnt in enumerate(contours):
        # approximate the contour
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        # if the shape got convex edges
        # & filter contour by 4angles shape
        if not cv2.isContourConvex(approx) or len(approx)!=4:
            continue
        # if that not a parallelogramm...
        # if the length is between [20cm;50cm] the original shape
        # if a 30 cm ie taille(pixels)€[100*160;120;170]
        if not tools.isPerimeterOK(cv2.arcLength(approx,True)) :#or not isAreaOK(cv2.contourArea(approx)):
            continue
        # filter contour by almost one child
        # no parent?
        if hierarchie[0,i,2]!=-1 and hierarchie[0,i,3]==-1:
            cont.append(approx)
    # ATTENTION : making the assumption that the contour with the largest area is the barcoded region of the frame
    # the largest among those with exactly 4 corners and children
    if cont==[]:
	return None
    # printing the original image with all contours which passed filters
    return cont

# Grosse marge blanche pour que ca fonctionne "parfaitement"
def getTagBox_vEmilias(gray):
    edges3 = tools.canny_algorithm_v2(gray)
    (contours,hierarchie) = cv2.findContours(edges3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # if no contours were found, return None
    if len(contours) == 0:
        return None
    # otherwise, sort the contours by area and compute the rotated
    # the contours with the largest area appear at the front of the list
    # bounding box of the largest contour
    cont = list()
    """
    tessts = list()
    aries = list()
    truc = list()
    i01 = gray.copy()
    cv2.drawContours(i01, contours, -1, (0, 255, 0), 4)
    cv2.imshow("found tag cont", i01)
    """
    # for each contour, computing an approximation of this same contour as a polyedre
    for i,cnt in enumerate(contours):
        # approximate the contour
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        # if the shape got convex edges
        # & filter contour by 4angles shape
        # if that not a parallelogramm...
        if len(approx)!=4 or not cv2.isContourConvex(approx):
            continue
        #tessts.append(approx)
        # if the length is between [20cm;50cm] the original shape
        # if the perimeter is ok ie taille(pixels)€[100*160;120;170]
        if not tools.isPerimeterOK(peri) :
            continue
        if not tools.isAreaOK(cv2.contourArea(approx)):
            continue
        # if the contour isn't a rectangle in the right orientation
        #aries.append(approx)

        if not tools.verify_measures(approx):
            continue
        """
        gray1 = gray.copy()
        cv2.drawContours(gray1, [approx], -1, (0, 255, 0), 3)
        cv2.imshow("drawn", gray1)
        truc.append(approx)
        """
        if not tools.contour_out_the_list(approx,cont):
            continue
        # filter contour by almost one child
        # no parent?
        if hierarchie[0,i,2]!=1: #tools.verify_hierarchy(hierarchie[0], i):
            cont.append(approx)
        #cv2.waitKey(0)
    """
    i1 = gray.copy()
    cv2.drawContours(i1, tessts, -1, (0, 255, 0), 4)
    cv2.imshow("found tag cont parallelogramme", i1)
    i2 = gray.copy()
    cv2.drawContours(i2, truc, -1, (0, 255, 0), 4)
    cv2.imshow("found tag cont measures ratio", i2)
    i3 = gray.copy()
    cv2.drawContours(i3, aries, -1, (0, 255, 0), 4)
    cv2.imshow("found tag cont perimetre", i3)
    """

    #cv2.waitKey(0)

    if cont==[]:
        return None
    return cont
