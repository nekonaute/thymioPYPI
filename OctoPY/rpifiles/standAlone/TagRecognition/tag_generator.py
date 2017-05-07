# -*- coding: utf-8 -*-
"""
Created on Sat May 14 22:25:36 2016

@author: emilie
"""
import cv2, tools, os
from optparse import OptionParser

if not os.path.exists(tools.TAGS_PATH):
        os.makedirs(tools.TAGS_PATH)
    
# getting back args
parser = OptionParser()
parser.add_option("-t", "--tag", dest="idBot", help="generate the four tags with the same ID needed for a single Robot")
(options, args) = parser.parse_args()

if (options.idBot is None):
    print "You have to enter an Id"
    exit(1)
ID_ROBOT = 0
try:
    ID_ROBOT = int(options.idBot)
except:
    print "The entered Id must be an integer"
    exit(1)

#id_top_left=(50,47)
#id_bottom_right=(175,172)
id_top_left=(48,51)
id_bottom_right=(177,175)

dir_top_left=(50,194)
dir_bottom_right=(177,252)

def draw_dir(img,dir_top_left,dir_bottom_right) :
    #taillew = dir_bottom_right[0]-dir_top_left[0]
    #tailleh = dir_bottom_right[1] - dir_top_left[1]
    middlew = (dir_bottom_right[0]+dir_top_left[0])/2
    img_left = img.copy()
    img_right = img.copy()
    img_back = img.copy()
    for y in range(dir_top_left[0],dir_bottom_right[0],1) :
        for x in range(dir_top_left[1],dir_bottom_right[1],1) :
            img_back[x][y] = 0
            if y <= middlew :
                img_right[x][y] = 0            
            else:
                img_left[x][y] = 0
    
    return img_right,img_left,img_back

def draw_id(img,id_top_left,id_bottom_right) :
    taillew = id_bottom_right[0]-id_top_left[0]
    tailleh = id_bottom_right[1] - id_top_left[1]
    caseW = taillew /tools.NB_COL_CASE
    caseH = tailleh / tools.NB_LIGN_CASE
    expoMax = (tools.NB_LIGN_CASE*tools.NB_COL_CASE)-1
    res = 0
    op = ID_ROBOT
    expo = []
    for i in range(expoMax,-1,-1) :
        res = op - 2**i
        if res >= 0 :
            op = res
            expo.append(1)
        else :
            expo.append(0)
    coordXmin = id_top_left[0]
    coordYmin = id_top_left[1]
    coordXm = coordXmin
    coordYm = coordYmin
    cpt = 0
    for caseNb in expo :
            deltaX = cpt % tools.NB_COL_CASE *caseW
            deltaY = cpt / tools.NB_LIGN_CASE *caseH  # partie entiere
            resXmin = coordXm + deltaX
            resYmin = coordYm + deltaY
            resXmax = coordXm + deltaX+ caseW
            resYmax = coordYm + deltaY+ caseH
            cpt += 1
            for y in range(resXmin,resXmax,1) :
                for x in range(resYmin,resYmax,1) :
                    if caseNb == 1 :
                        img[x][y] = 0
                    else:
                        break
    return img

try:
    img = cv2.imread(tools.TEMPLATE_PATH+ 'tag_template_init.png',0)
    
    img = draw_id(img,id_top_left,id_bottom_right)
    
    cv2.imwrite(tools.TAGS_PATH+"tag_{}_front.png".format(ID_ROBOT),img)
    
    img_right,img_left,img_back = draw_dir(img,dir_top_left,dir_bottom_right)
    
    cv2.imwrite(tools.TAGS_PATH+"tag_{}_right.png".format(ID_ROBOT),img_right)
    cv2.imwrite(tools.TAGS_PATH+"tag_{}_left.png".format(ID_ROBOT),img_left)
    cv2.imwrite(tools.TAGS_PATH+"tag_{}_back.png".format(ID_ROBOT),img_back)
except:
    pass
