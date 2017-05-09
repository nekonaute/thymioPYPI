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

TAG_ID_ERROR = -1

lk_params = dict(
            winSize  = (10,10), # max extimation of movement
            maxLevel = 4, # LK hypothese is true at lowest level
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            )

def estimate_next_positions(prec_frame,curr_frame,prec_contours,actual_side_size=1):
    prec_points = np.float32(prec_contours).reshape(-1,1,2)
    global lk_params
    next_points, status, err = cv2.calcOpticalFlowPyrLK(prec_frame,curr_frame,prec_points)
    n_pts = len(next_points)/4
    next_contours, next_distances, next_rotations = [],[],[]
    status_contours = np.zeros(n_pts,np.dtype(np.bool))
    for i in xrange(n_pts):
        if len(next_points[i*4:(i*4)+4])==4 and np.all(status[i*4:(i*4)+4]):
            status_contours[i] = True
            p1, p2, p3, p4 = next_points[i*4:(i*4)+4]
            p1, p2, p3, p4 = map(int,p1[0]),map(int,p2[0]),map(int,p3[0]),map(int,p4[0])
            contour = np.array([ [p1],[p2],[p3],[p4] ])
            rect = cnt2rect(contour)
            bb = bounding_box(contour)
            next_distances += [ estimate_distance(rect,actual_side_size=actual_side_size) ]
            next_rotations += [ estimate_rotation(bb) ]
            next_contours += [ contour ]
    return status_contours, next_contours, next_distances, next_rotations

def rad_to_deg(angle):
    # angle*(180/pi)
    return np.rad2deg(angle)

def deg_to_rad(angle):
    # angle*(pi/180)
    return np.deg2rad(angle)

def estimate_rotation(bounding_box):
    """
        estimate rotation using arctan
    """
    # x,y coord of topleft corner
    x,y,w,h = bounding_box
    rotation_arg = np.abs(1 - (h/float(w)))*2
    return rad_to_deg( np.arctan(rotation_arg) )

def estimate_distance(rect,actual_side_size=2,frame_h=1080,v_aov=41.,eps=10e-3):
    """
        rect type must be np.zeros((4, 2), dtype = np.float32)
        follow this order for input
        (tl, tr, br, bl) = rect
        actual_side_size: actual_side_size of the tag
        v_aov: angle of view for RASPBERRY camera
        frame_h: video port height

        default vales referece to the pi camera module v.1:
        http://elinux.org/Rpi_Camera_Module#Technical_Parameters_.28v.2_board.29

        returned measures are in cm
    """
    (tl, tr, br, bl) = rect
    l_side = np.sqrt(np.dot((tl-bl),(tl-bl).T))
    r_side = np.sqrt(np.dot((tr-br),(tr-br).T))
    appearent_side_size = np.max([l_side,r_side])
    projected_angle = (v_aov/frame_h)*(appearent_side_size+eps)
    # tag values are in cm
    # plus approximating the arc with a segment leads to different values
    # after taking measures the problem is resolved "empirically"
    rect_coeff = 14.1785
    return actual_side_size/float(projected_angle)*rect_coeff

def identify_tag_id(tag_image,tiles_x=3,tiles_y=3):
    """
        Calculate the nine bit value of the identification tag.
        The most significant bit is on the top left, the others follows as shown:

         ------- ------- -------
        | bit_0 | bit_3 | bit_6 |
        |       |       |       |
         ------- ------- -------
        | bit_1 | bit_4 | bit_7 |
        |       |       |       |
         ------- ------- -------
        | bit_2 | bit_5 | bit_8 |
        |       |       |       |
         ------- ------- -------

    """
    # normalize tag
    min_val = np.min(tag_image)
    tag_image = tag_image-min_val
    max_val = np.max(tag_image)
    tag_image = (tag_image/float(max_val))*255.
    tag_image[tag_image>127] = 255
    tag_image[tag_image<=127] = 0

    y,x = tag_image.shape
    dx,dy = x/(tiles_x*2),y/(tiles_y*2)
    dtau = dx/3 if dx/3 >0 else 1 # witdth of the filter applied to sampling
    id_tag = 0
    for i in xrange(tiles_x):
        for j in xrange(tiles_y):
            crdx, crdy = (2*i)*dx + dx,(2*j)*dy + dy
            sample = np.sum(tag_image[crdy-dtau:crdy+dtau,crdx-dtau:crdx+dtau])/((dtau**2)*255.)
            tag_image[crdy-dtau:crdy+dtau,crdx-dtau:crdx+dtau] = 127
            # thresholding the noise
            if sample > 0.75:
                bit = 1
            elif sample < 0.25:
                bit = 0
            else:
                return TAG_ID_ERROR
            id_tag += bit *2**(i*tiles_x+j)
    return id_tag

def threshold_tag(tag_image):
    """
        This step is necessary to tag identification.

        The tag is modeled as a 2D binary NRZ signal.
        Binary simbols are in {min gray,max gray}
        the optimal threshold maximizing the SNR is at the
        middle of the amplitudes.
    """
    thresh = (np.max(tag_image)+np.min(tag_image))/2.
    ret,thresh = cv2.threshold(tag_image,thresh,255,0)
    return thresh

# using kernprof -v -l for profiling
# @profile
def rectify_perspective_transform(image,rect,maxWidth=30,maxHeight=30):
    """
        Finds and apply inverse perspective transformation for image rectification.

        http://docs.opencv.org/2.4/modules/imgproc/doc/geometric_transformations.html?highlight=warpaffine#cv2.getAffineTransform

        bleed: cropping contour in pixel from each side.
        bottom_off: offset from the identification tag to the botton tag.

        In certain cases the rotation can prevent the tag to be rectified correctly
        by checking the diagonal and antidiagonal of the 2x2 matrix where the
        cofficients proportional to the roation are stored we can use a bleed
        margin to correcte certaing distortions.
         _______________
        |     bleed     |
        |   ---------   |
        |  |         |  |
        |  |         |  |  tag
        |  |         |  |
        |   ---------   |
        |_______________|

    """
    dst = np.array([
    	[0, 0],
    	[maxWidth - 1, 0],
    	[maxWidth - 1, maxHeight - 1],
    	[0, maxHeight - 1]],
        dtype = np.float32)

    # calculate the perspective transform matrix and warp
    M = cv2.getPerspectiveTransform(rect, dst)
    # correction:
    # sometimes correcting rotated images introduces errors
    diag_vals = np.abs(M[0,0] + M[1,1])
    anti_diag_vals = np.abs(M[0,1] + M[1,0])
    bleed = 1
    if diag_vals > anti_diag_vals:
        bleed = maxWidth/5
    # attention opencv returns inveresd h and w!!!
    warp = cv2.warpPerspective(image, M, (maxWidth,maxHeight))
    warp_tag = warp[bleed:maxHeight-bleed,bleed:maxWidth-bleed]
    return warp_tag

# using kernprof -v -l for profiling
# @profile
CNT,IDS,DST,ROT = 0,1,2,3
def detect_tags(gray_image, ar, actual_side_size=2, sigma=0.3):
    edge_image = edge_detection(gray_image, sigma=sigma)
    tags_contours = find_tags_contours(edge_image,ar)
    tags_ids, tags_distances, \
    tags_rotations, tags_bounding_boxes, tags_aligned = [],[],[],[],[]
    for tag_contour in tags_contours:
        tag_rect = cnt2rect(tag_contour)
        tag_aligned = rectify_perspective_transform(gray_image,tag_rect)
        # append new values
        tags_ids += [ identify_tag_id(tag_aligned) ]
        tags_distances += [ estimate_distance(tag_rect, actual_side_size=actual_side_size) ]
        tag_bounding_box = bounding_box(tag_contour)
        tags_rotations += [ estimate_rotation(tag_bounding_box) ]
        tags_bounding_boxes += tag_bounding_box
        tags_aligned += [ tag_aligned ]
    return tags_contours, tags_ids, tags_distances, tags_rotations

# using kernprof -v -l for profiling
# @profile
def edge_detection(gray_image, sigma=0.3):
    """
        Use Canny edge detction algorythm
    """
    # compute the mean of image
    y,x = gray_image.shape
    l_image = gray_image[y/3:y-(y/3),(x/3):x/2-((x/3))]
    r_image = gray_image[y/3:y-(y/3),x/2-(x/3):x-(x/3)]
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
def find_tags_contours(edge_image, ar, sigma=0.3, eps=20):
    """
    Tag Robust detection is achieved by creating a series of tests
    There are 5 layers of countours for each tag. Tag info is stored in the
    innermost contour.

        level -------------------------------
        | next level-----------------------  |
        | | next level-------------------  | |
        | | | next next level----------  | | |
        | | | | next next level----  | | | | |

    ar is the area_ratio of the tags countours.
    eps and sigma are found experimentally:
        -sigma is the variance of the area_ratio.
        -eps is the minimum area in pixels for a contour to be considered.
    """
    # this function is horrible...
    contours, hierarchy = image_utils.findContours(edge_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
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

            # level
            child = hierarchy[curr][2]
            if child!=-1 and child<N-1:
                if is_tag_cnt(contours[curr],contours[child],ar,sigma,eps):
                    child_approxTop = approx_cnt(contours[child])
                    if len(child_approxTop) == 4:
                        # next level
                        next_curr = hierarchy[child][2]
                        next_child = hierarchy[next_curr][2]
                        if next_child!=-1 and next_child<N-1:
                            next_curr_approxTop = approx_cnt(contours[next_curr])
                            if len(next_curr_approxTop) == 4:
                                if is_tag_cnt(next_curr_approxTop,contours[next_child],ar,sigma,eps):
                                    next_child_approxTop = approx_cnt(contours[next_child])
                                    if len(next_child_approxTop) == 4:
                                        # next next Level
                                        next_next_curr = hierarchy[next_child][2]
                                        next_next_child = hierarchy[next_next_curr][2]
                                        if next_next_curr!=-1 and next_next_curr<N-1 and next_next_child!=-1:
                                            next_next_curr_approxTop = approx_cnt(contours[next_next_curr])
                                            next_next_child_approxTop = approx_cnt(contours[next_next_child])
                                            if len(next_next_curr_approxTop)==4 and len(next_next_child_approxTop)==4:
                                                # next next next level
                                                next_next_next_curr = hierarchy[next_next_child][2]
                                                next_next_next_child = hierarchy[next_next_next_curr][2]
                                                if next_next_next_curr!=-1 and next_next_next_child!=-1:
                                                    next_next_next_curr_approxTop = approx_cnt(contours[next_next_next_curr])
                                                    next_next_next_child_approxTop = approx_cnt(contours[next_next_next_child])
                                                    if is_tag_cnt(next_next_next_curr_approxTop,next_next_next_child_approxTop,ar,sigma,eps) and \
                                                        len(next_next_next_curr_approxTop)==4 and len(next_next_next_child_approxTop)==4:
                                                        # check level
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
                                                            if not occour[next_next_curr]:
                                                                occour[next_next_curr] = True
                                                            if not occour[next_next_child]:
                                                                occour[next_next_child] = True
                                                            if not occour[next_next_next_curr]:
                                                                occour[next_next_next_curr] = True
                                                            if not occour[next_next_next_child]:
                                                                occour[next_next_next_child] = True
                                                                # save deepest contour
                                                                tag_contours += [next_next_next_child_approxTop]

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
