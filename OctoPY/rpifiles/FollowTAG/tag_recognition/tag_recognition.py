import cv2
import numpy as np
from numpy import linalg as lnag
import image_utils


#################################################################################
#                      TAG DETECION FOR RASPBERRY v.1.0                         #
#################################################################################

info = "This is a collection of functions used to detect, identify and estimate metrics\n"
info +="the tag description is in the settings.py file"

def __info__():
    return info

#################################################################################

TAG_ID_ERROR = 99999

def rad_to_deg(angle):
    # angle*(180/pi)
    return np.rad2deg(angle)

def deg_to_rad(angle):
    # angle*(pi/180)
    return np.deg2rad(angle)

def estimate_rotation(rect):
    """
        rect type must be np.zeros((4, 2), dtype = np.float32)
        follow this order for input
        (tl, tr, br, bl) = rect
    """
    (tl, tr, br, bl) = rect
    l_side = np.sqrt(np.dot((tl-bl),(tl-bl).T))
    r_side = np.sqrt(np.dot((tr-br),(tr-br).T))
    b_side = np.sqrt(np.dot((bl-br),(bl-br).T))
    up_side = np.sqrt(np.dot((tl-bl),(tl-bl).T))
    sign = 1
    if l_side > r_side:
        return -l_side/float(b_side)#-rad_to_deg( np.arctan(np.sqrt(l_side/float(b_side))) )
    return l_side/float(b_side)#rad_to_deg( np.arctan(np.sqrt(r_side/float(b_side))) )

def estimate_distance(rect,actual_side_size=2,frame_h=1080,v_aov=41.,eps=10e-3):
    """
        rect type must be np.zeros((4, 2), dtype = np.float32)
        follow this order for input
        (tl, tr, br, bl) = rect
        t_a: the actual tag diagonal
        v_aov: angle of view for RASPBERRY camera
        frame_h: video port height

        default vales referece to the pi camera module v.1:
        http://elinux.org/Rpi_Camera_Module#Technical_Parameters_.28v.2_board.29
    """
    (tl, tr, br, bl) = rect
    l_side = np.sqrt(np.dot((tl-bl),(tl-bl).T))
    r_side = np.sqrt(np.dot((tr-br),(tr-br).T))
    appearent_side_size = np.max([l_side,r_side])
    projected_angle = (v_aov/frame_h)*(appearent_side_size+eps)
    # tag values are in cm
    # plus approximating the arc with a segment leads to different values
    # after taking measures the problem is resolved "empirically"
    rect_coeff = 0.141785
    return actual_side_size/float(projected_angle)*rect_coeff

def identify_tag(tag_image,tiles_x=3,tiles_y=3):
    """
        tag are 3x4 array, last row is parity bit,
    """
    y,x = tag_image.shape
    dx,dy = x/(tiles_x+1),y/(tiles_y+2)
    dtau = 3
    id_tag = 0
    for i in xrange(tiles_x):
        for j in xrange(tiles_y):
            crdx, crdy = (1+i)*dx,(1+j)*dy
            sample = np.sum(tag_image[crdy-dtau:crdy+dtau,crdx-dtau:crdx+dtau])/(16.*255.)
            tag_image[crdy-dtau:crdy+dtau,crdx-dtau:crdx+dtau] = 127
            # thresholding the noise
            if sample > 0.75:
                bit = 1
            elif sample < 0.25:
                bit = 0
            else:
                #notag
                return TAG_ID_ERROR
            id_tag += bit *2**(i+j*2)
    return id_tag

def threshold_tag(tag_image):
    """
        once a tag image is found binarize the input.
        as we model the tag signal as formant code composed
        by a rect function and 2 amplitudes (min gray,max gray)
        the optimal threshold maximizin the SNR is at the
        middle of the amplitudes.
    """
    thresh = (np.max(tag_image)+np.min(tag_image))/2.
    ret,thresh = cv2.threshold(tag_image,thresh,255,0)
    return thresh

# using kernprof -v -l for profiling
# @profile
# Total time: 0.00845 s on Pi3
def rectify_tag(image,rect,auto_size=False,maxWidth=100,maxHeight=100,bleed=5,bottom_off=75):
    """
    """
    dst = np.array([
    	[0, 0],
    	[maxWidth - 1, 0],
    	[maxWidth - 1, maxHeight - 1],
    	[0, maxHeight - 1]],
        dtype = np.float32)

    # calculate the perspective transform matrix and warp
    M = cv2.getPerspectiveTransform(rect, dst)
    # attention opencv returns inveresd h and w!!!
    #warp = cv2.warpPerspective(image, M, (maxWidth, bottom_off+maxHeight))      # 85.7
    # separate_ the tag body from the tag orientation section
    #warp_tag = warp[bleed:maxHeight-bleed,bleed:maxWidth-bleed]
    #orient_tag = warp[maxHeight+bleed*3:,:]
    #return warp_tag, orient_tag
    warp = cv2.warpPerspective(image, M, (maxWidth,maxHeight))
    return warp[bleed:maxHeight-bleed,bleed:maxWidth-bleed]

# using kernprof -v -l for profiling
# @profile
def detect_tags(gray_image, ar, actual_side_size=2, sigma=0.3):
    edge_image = detect_tag_contours(gray_image, sigma=sigma)
    tags_contours = find_tags_contours(edge_image,ar)

    tags_aligned, tags_ids, tags_distances, tags_rotations = [],[],[],[]
    for tag_contour in tags_contours:
        tag_rect = cnt2rect(tag_contour)
        tag_aligned = rectify_tag(gray_image,tag_rect)
        tag_aligned = threshold_tag(tag_aligned)
        # append new values
        tags_ids += [ identify_tag(tag_aligned) ]
        tags_distances += [ estimate_distance(tag_rect, actual_side_size=actual_side_size) ]
        tags_rotations += [ estimate_rotation(tag_rect) ]
        tags_aligned += [ tag_aligned ]
    return tags_contours,tags_aligned,tags_ids,tags_distances,tags_rotations

# using kernprof -v -l for profiling
# @profile
def detect_tag_contours(gray_image, sigma=0.3):
    # compute the median of the single channel pixel intensities
    y,x = gray_image.shape
    l_image = gray_image[100:y-100,100:x/2-100]
    r_image = gray_image[100:y-100,x/2-100:x-100]
    v = (np.mean(l_image) + np.mean(r_image))/2.
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edge_image = cv2.Canny(gray_image, lower, upper)
    return edge_image

def is_tag_cnt(cnt_p, cnt_c, ar, sigma, eps):
    area_1 = cv2.contourArea(cnt_p)
    area_2 = cv2.contourArea(cnt_c)
    if area_1 > eps and area_2 > eps: # div by zero check
        area_ratio = area_1/float(area_2)
        return area_ratio <= ar+sigma and area_ratio >= ar-sigma
    return False

# using kernprof -v -l for profiling
# @profile
def find_tags_contours(edge_image, ar, sigma=0.3, eps=20, approx=cv2.CHAIN_APPROX_NONE):
    """
        CHAIN_APPROX_NONE fast result and better response for skewed tags.

        ar is the area_ratio of the tags markers (3 inscribed squares)
        eps and sigma are found experimentally:
            -sigma is the variance of the area_ratio.
            -eps is the minimum area in pixels for a contour to be considered.
    """
    contours, hierarchy = cv2.findContours(edge_image,cv2.RETR_TREE,approx)     # 27.6
    if hierarchy is None:
        return contours
    tag_contours = []
    N = len(contours)
    hierarchy = hierarchy[0]
    occour = np.zeros(N,np.dtype(np.bool))
    for curr in xrange(1,N):
        if not occour[curr]:
            # we do not approximate first contour
            # following depths will be checked
            # if all checks are clear than it will check for the parent
            # this saves up a lot of computation.
            child = hierarchy[curr][2]
            if child!=-1 and child<N-1:
                child_approxTop = approx_cnt(contours[child])
                if len(child_approxTop) == 4 and is_tag_cnt(contours[curr],contours[child],ar,sigma,eps):
                    next_curr = child+1
                    next_curr_approxTop = approx_cnt(contours[next_curr])
                    if len(next_curr_approxTop) == 4:
                        next_child = hierarchy[next_curr][2]
                        if next_child!=-1 and next_child<N-1:
                            next_child_approxTop = approx_cnt(contours[next_child])
                            if len(next_child_approxTop) == 4 and is_tag_cnt(contours[next_curr],contours[next_child],ar,sigma,eps):
                                curr_approxTop = approx_cnt(contours[curr])
                                if len(curr_approxTop) == 4:
                                    if not occour[curr]:
                                        occour[curr] = True
                                    if not occour[child]:
                                        occour[child] = True
                                    if not occour[next_curr]:
                                        occour[next_curr] = True
                                    if not occour[next_child]:
                                        occour[next_child] = True
                                        # save deepest contour
                                        tag_contours += [next_child_approxTop]
    return tag_contours


def cnt2rect(cnt):
    pts = cnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = np.float32)
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # the order now is
    # (tl, tr, br, bl) = rect
    return rect

def approx_cnt(cnt):
    peri = cv2.arcLength(cnt, True)
    approxTop = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    return approxTop

def pre_processing_image(image):
    gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return gray_image

def bounding_box(cnt):
    return cv2.boundingRect(cnt)

def min_circle(cnt):
     return cv2.minEnclosingCircle(cnt)

def rot_bounding_box(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    return box

def k_means(image,k=3):
    points = np.float32(image.reshape((-1,1)))
    term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, labels, centers = cv2.kmeans(points, k, term_crit, 10, 0)
    return ret, labels, centers
