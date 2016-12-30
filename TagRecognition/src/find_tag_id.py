# -*- coding: utf-8 -*-
import numpy as np
from math import fabs, asin, degrees
import tools
import time
import cv2

# Robot's informations

"""
identification du robot    
renvoie l'id lu a partir du tagId 
qui est la partie identification du robot

Contexte : tous les filtres ont été appliqués (img thresholdee),
        l'image correspond a l'identifiant du robot sur le tag
"""
import time

def read_id(tagId):
    tagId = tools.apply_filters(tagId)
    #thresh = cv2.erode(thresh, None, iterations = 1) # usefull?
    # size of the image
    height,width = tagId.shape
    # step in pixel for each lign (resp. col)
    pas_lignes = int(float(height)/tools.NB_LIGN_CASE)
    pas_cols = int(float(width)/tools.NB_COL_CASE)
    # the pixels we want to ignore
    forgotten = int(pas_lignes*0.15)
    # lambda fct to compute the id
    puiss = lambda x:2**x
    # computation of the id
    id_bot = 0
    
    # foreach case of the id area
    # starting with the case in right bottom (index 0 for the reading)
    # ending with the one in left top (index 8 for the reading)
    for coord in reversed(range(tools.NB_COL_CASE*tools.NB_LIGN_CASE)):
    	# deltaX : column number   	
        deltaX = coord % tools.NB_COL_CASE
        # deltaY : lign number
        deltaY = coord / tools.NB_COL_CASE # partie entiere
        # i : beginning of the deltaY case (num lign in pixels)
        i = deltaY*pas_lignes
        # j  : beginning of the deltaX case (num col in pixels)
        j = deltaX*pas_cols
        # computing the right index to calculate the id
        ind_id = tools.NB_COL_CASE*tools.NB_LIGN_CASE-1-coord
        # getting the case array
        sub_tab = tagId[i+forgotten:i+pas_lignes-forgotten,j+forgotten:j+pas_cols-forgotten]
        # computing the round mean of this case
    	mean = (cv2.mean(sub_tab)[0])/255
    	# getting a 0 and 1 array image
        val = int(round(mean))
        # if the case is black
        if val==0:
            # using the index to evaluate
       	    id_bot += puiss(ind_id)
    # end for
    ###
    return id_bot

def read_dir(tagDir):
    tagDir = tools.apply_filters(tagDir)
    #thresh = cv2.erode(thresh, None, iterations = 1) # usefull?
    # size of the image
    height,width = tagDir.shape
    # step in pixel for each lign (resp. col)
    pas_cols = int(width/2.)
    # the pixels we want to ignore
    forgotten = int(height*0.30)
    # computation of the id
    dir_bot = ""
    # getting a 0 and 1 array image
    tab = tagDir/255
    # foreach case of the direction area
    for coord in range(2):
        # j : beginning of the coord case (num col in pixels)
    	j = coord*pas_cols
        # getting the case array
        sub_tab = tab[forgotten:height-forgotten,j+forgotten:j+pas_cols-forgotten]
        # computing the round mean of this case
        val = int(round(cv2.mean(sub_tab)[0]))
        # using the index to evaluate
        val = 1-val
        dir_bot += str(val)
    # end for
    ###
    return dir_bot
    
def get_direction(direction):
    if direction == "00":
        return "front"
    elif direction == "10":
        return "right"
    elif direction == "01":
        return "left"
    elif direction == "11":
        return "back"

# define the coordinates of the white area including the 2 children containing datas
def coord_min_max(data_enfant):
    x1 = 99999
    y1 = 99999
    x2 = 0
    y2 = 0
    for coord in enumerate(data_enfant):
        if x1 > coord[1][0]: 
            x1 = coord[1][0]
        elif x2 < coord[1][0]:
            x2 = coord[1][0]
        if y1 > coord[1][1]:
            y1 = coord[1][1]
        elif y2 < coord[1][1]:
            y2 = coord[1][1]
    return x1, y1, x2, y2

# filter the duplicate coordonates defining children corners, return only 4 points
def filter_duplicate(tEnfant):
    filteredList = []
    for ind, e in enumerate(tEnfant):
    	x = e[0][0]
        y = e[0][1]
        doublon = False
        for el in enumerate(filteredList):
            if fabs(x - el[1][0]) < 6 and fabs(y - el[1][1]) < 6:
                #    print " doublon!! "
                doublon = True
        if not doublon:
            filteredList.append([x, y])
    return filteredList

def separate_children(hierarchy,img1, conts):
    # **[Next, Previous, First_Child, Parent]**
    idChild1 = idChild2 = -2
    cont_id = cont_dir = None
    height,width = img1.shape
    peri_dad = (height+width)*2
    area_dad = height*width
    for i, h in enumerate(hierarchy):
        cont = None
        img = tools.color_gray_img(img1,to_gray=False)
        next = h[0]
        prev = h[1]
        son = h[2]
        dad = h[3]
        if (next!=-1 or prev!=-1) and dad!=-1:
            # it is an interesting contour
            child, cont = tools.verifChild(h,conts[i], peri_dad,area_dad)
            # we'll take it
            if child==1: 
                idChild1 = i
                cont_id = cont
            elif child==2:
                idChild2 = i
                cont_dir = cont
        # case : we found the two children
        if idChild1!=-2 and idChild2!=-2:
            break
        """
        print "sa hier ",h
        cv2.drawContours(img,[conts[i]],-1,(255,255,0),2)
        cv2.imshow("separation children",img)
        if not cont is None:
            cv2.imshow('part',get_part(img,cont))
        cv2.waitKey(0)
        """
    return (idChild1,cont_id), (idChild2,cont_dir)

def get_part(img,contour):
    # slower
    #epsilon = 0.04*cv2.arcLength(contour, True) # aproximation accuracy
    #approx = cv2.approxPolyDP(contour, epsilon, True)
    tag = tools.imgHomot(img,contour)
    return tag

def get_corners(contour,height,width):
    """
    Return a 4 contours array arranged this way:
    top-left,top-right,bottom-right, bottom-left
    """
    contour = np.array([x[0] for x in contour])
	# set to opposite value possible
    top_left = [width,height]
    top_right = [0,height]
    bot_right = [0,0]
    bot_left = [width,0]
    for val in contour:
        val = val[0]
        if val[0]<top_left[0] and val[1]<top_left[1]:
            top_left = val
        if val[0]<bot_left[0] and val[1]>bot_left[1]:
            bot_left = val
        if val[0]>bot_right[0] and val[1]>bot_right[1]:
            bot_right = val
        if val[0]>top_right[0] and val[1]<top_right[1]:
            top_right = val
    print "Corners",[top_left,top_right,bot_right,bot_left]
    #return [top_left,top_right,bot_right,bot_left]
    print type(contour[0][0]),contour[0,0], len(contour)

def contour_min_max(contour):
    """
    Return the xmin ymin and xmax ymax values of the contour
    """
    #contour = np.array([x[0] for x in contour])
    min_xy = contour[0,0]
    max_xy = contour[2,0]
    """
    for i in range(1,len(contour)):
    c = contour[i]
    if c[0]<=min_xy[0] and c[1]<=min_xy[1]:
    min_xy = c
    if c[0]>=max_xy[0] and c[1]>=max_xy[1]:
    max_xy = c
    """
    return min_xy, max_xy

def centroid(contour):
	minxy,maxxy = contour_min_max(contour)
	midw = minxy[0]+((maxxy[0]-minxy[0])/2)
	midh = minxy[1]+((maxxy[1]-minxy[1])/2)
	return midw,midh

def compute_side_distance(img,cont_tag,tag_size):
    _,img_w = img.shape
    tag_h,tag_w = tag_size
    # computing the image reference center
    midd_w = img_w/2
    # getting the centroid of the id of the tag
    tagx,_ = centroid(cont_tag)
    # distance ("produit en croix")
    dist = dist_h = tools.DIST_MIN*tools.HEIGHT_MIN/float(tag_h) # theoreme 3D (DDD)
    """
    print "DISTANCE H = ",dist
    print "DISTANCE W = ",tools.DIST_MIN*tools.WIDTH_MIN/tag_w
    print "DISTANCE P = ",tools.DIST_MIN*(tools.HEIGHT_MIN+tools.WIDTH_MIN)/(tag_w+tag_h)
    print "DISTANCE A = ",tools.DIST_MIN*(tools.HEIGHT_MIN*tools.WIDTH_MIN)/(tag_w*tag_h)
    """
    if dist == 0 :
        return (0,0)
    # side = angle <- trigonometry (sinus : opposite/hypothenusis)
    # the distance from center line of the image to the tag centroid
    pix_midd = midd_w-tagx # opposite
    dist_midd = pix_midd*tools.TAG_HEIGHT/tools.HEIGHT0
    #dist_midd = pix_midd/tools.CM_PIX
    angle = asin(dist_midd/float(dist))
    deg = degrees(angle)
    return dist,deg
	
# extract id and direction of the robot based on the tag
def obtain_tag_info(img, tag, contours, hierarchy, tag_cont):
    """
    Return the tuple id (int), direction (string)
    Optionnally the distance and angle
    """
    sep = time.time()
    (idChild1, cont_id), (idChild2, cont_dir) = separate_children(hierarchy[0],tag,contours)
    # get_corners(contours[idChild1],*img.shape)
    # cv2.waitKey(0)

    if idChild1==-2 and idChild2==-2:
        # no interessant contour was found
        #print "No contour"
        return None
    id_bot = direct = None
    if idChild1!=-2:
        part1 = time.time()
        # retrieving the id of the robot
        id_part = get_part(tag,cont_id)
        #print "APPROX = ", cont_id
        read1 = time.time()
        #cv2.imshow("appprox1",id_part)
        id_bot = read_id(id_part)
    if idChild2!=-2:
        part2 = time.time()
        # retrieving the direction of the robot
        dir_part = get_part(tag,cont_dir)
        read2 = time.time()
        direct = read_dir(dir_part)
        #cv2.imshow("appprox2",dir_part)
    print "FOUND BOT ==== ",id_bot,direct
    angle_robot = tools.robot_angle(tag_cont,direct)
    minxy, maxxy = contour_min_max(tag_cont)
    tag_size = (maxxy[1]-minxy[1],maxxy[0]-minxy[0])
    # retrieving the distance and the side (+x:left,0:in front,-y:right) where the tag is found from me
    dist, img_side = compute_side_distance(img, tag_cont,tag_size)
    side = tools.switch_side_img(img_side)
    return id_bot,direct, angle_robot, dist, side
    
def is_real_tag(tag):
    """
    Checking is the read tag really is a tag (not a window)
    Return True if the tag is a good one, and the center of the crop tag (only id+dir part)
    """
    height, width = tag.shape
    supp = tools.SUPP_MARGIN
    wmargin = tools.OCCLUSION_MARGIN * width / tools.TAG_WIDTH
    hmargin = tools.OCCLUSION_MARGIN * height / tools.TAG_HEIGHT
    # computing the edges percentages
    lign_per = hmargin / height
    col_per = wmargin / width
    height -= 1
    width -= 1
    # retrieving the rightmost border
    lign1 = tag[0:height*lign_per,0+supp:width]
    # retrieving the leftmost border
    lign2 = tag[height-height*lign_per:height,0+supp:width]
    # retrieving the upper border
    col1 = tag[0:height,0:width* col_per]
    # retrieving the lower border
    col2 = tag[0:height,width-width*col_per:width]
    
    # thresholding every edge for a better comparison
    lign1 = tools.thresholding(lign1)
    lign2 = tools.thresholding(lign2)
    col1 = tools.thresholding(col1)
    col2 = tools.thresholding(col2)
    """
    cv2.imshow("lign1", lign1)
    cv2.imshow("lign2", lign2)
    cv2.imshow("col1", col1)
    cv2.imshow("col2", col2)
    #cv2.waitKey(0)
    """
    w_col = width*col_per
    h_col = height
    w_lign = width
    h_lign = height*lign_per
    nb_edges_ok = 0. # black edges are 0.5; whiteblack are 1 -> 8 edges counted
    isBlack = lambda x : x<255/3
    isWhite = lambda x : x>=255/3
    for fact in range(3):
        moys = []
        # for ligns
        j_lign = w_lign*fact/3
        # lign1
        l1_moy = cv2.mean(lign1[0+supp:h_lign-supp,j_lign+supp:j_lign-supp+w_lign/3])[0]
        moys.append(l1_moy)
        # lign2
        l2_moy = cv2.mean(lign2[0+supp:h_lign-supp,j_lign+supp:j_lign-supp+w_lign/3])[0]
        moys.append(l2_moy)
        # for columns
        i_col = h_col*fact/3
        # col1
        c1_moy = cv2.mean(col1[i_col+supp:i_col-supp+h_col/3,0+supp:w_col-supp])[0]
        moys.append(c1_moy)
        # col2
        c2_moy = cv2.mean(col2[i_col+supp:i_col-supp+h_col/3,0+supp:w_col-supp])[0]
        moys.append(c2_moy)
        # if that's mainly black(-> moy<85) and fact!=1 (-> it's not the center of the edge)
        if fact!=1:
            nb_edges_ok += map(isBlack,moys).count(True)/2.
        else:
            nb_edges_ok += map(isWhite,moys).count(True)
    # returning whether the image really is a tag
    if (True if nb_edges_ok>=5.5 else False):
        # it is -> losing time with thresholding
        #thresh = tools.apply_filters(tag)
        #thresh = cv2.erode(thresh, None, iterations = 1) # usefull?
        tagCenter = tag[height*lign_per:height-height*lign_per,width* col_per:width-width*col_per]
        return True,tagCenter
    else:
        # it's not -> not loosing time
        return False, None
       
    
    
def lecture_tag(img,tag_found, tag_cont):
    # if the contour found aren't a real tag
    dt = time.time()
    is_tag, tag = is_real_tag(tag_found) # is_real_tag(thresh)
    if not is_tag:
        print "\t\t Not a real tag"
        return None
    print "\tIt's a real tag"
    ret = None  #[None,None,None,None, None, tag_cont]
    res = res2 = None
    thresh = tools.apply_filters(tag)
    # extract hierarchy of the tag
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # otherwhise, it is a real tag, we continue
    res = obtain_tag_info(img, tag, contours, hierarchy,tag_cont)
    # if the previous wasn't conclusive
    if res is None or res[0] is None or res[1] is None:
        canny = tools.canny_lecture(tag)
        contours, hierarchy = cv2.findContours(canny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        res2 = obtain_tag_info(img, tag, contours, hierarchy, tag_cont)
    if res is None :
        ret = res2
    elif res2 is None:
        ret = res
    else:
    	ret = list(res)
        ret[0] = res2[0] if res[0] is None else res[0]
        ret[1] = res2[1] if res[1] is None else res[1]
        ret[2] = res2[2] if res[2] is None else res[2]
        ret = tuple(ret)
    return ret
