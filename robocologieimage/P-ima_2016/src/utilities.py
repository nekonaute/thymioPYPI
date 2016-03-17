 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import cv2
import numpy as np
import json

def rgb2gray(mat):
    """ Converts an RGB image to grayscale, where each pixel
    now represents the intensity of the original image. """
    return cv2.cvtColor(mat, cv2.COLOR_RGB2GRAY)

def threshold(mat, th=0):
    """
    mat : mat matrix -> mat_b : Binary Image matrix thresholded
    """
    (th, mat_th) = cv2.threshold(mat, th, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return th, mat_th

def canny_algorithm(mat):
    """
    mat : mat matrix
    """

    # Blur
    #mat = cv2.medianBlur(cv2.medianBlur(mat, 3), 3)
    mat = cv2.GaussianBlur(mat, (5,5), 0)

	# Canny edge detection using the computed median
    v = np.median(mat); sigma = 0.20
    lower_thresh_val = int(max(0, (1.0 - sigma) * v))
    high_thresh_val = int(min(255, (1.0 + sigma) * v))
    mat = cv2.Canny(mat, lower_thresh_val, high_thresh_val)

    # Dilation/Erosion to close edges
    kernel = np.ones((2, 2), np.uint8)
    mat = cv2.dilate(mat, kernel, (-1, -1), iterations=1)
    mat = cv2.erode(mat, kernel,(-1, -1), iterations=1)

    return mat

def find_contours(mat_b):
    """
    mat_b : Binary Image matrix
    """
    width, height = mat_b.shape
    (mat_b, edges, hierarchy) = cv2.findContours(mat_b,
        mode=cv2.RETR_TREE,  method=cv2.CHAIN_APPROX_SIMPLE, offset=(0,0))

    marker_edges1, marker_edges2 = [], []
    for i in range(len(edges)):
        epsilon = 0.035*cv2.arcLength(edges[i], True)
        approx_curve = cv2.approxPolyDP(edges[i], epsilon, True)
        if not cv2.isContourConvex(approx_curve):
            continue
        if cv2.contourArea(approx_curve) < 100:
            continue
        if len(approx_curve) != 4:
            continue

        sorted_curve = np.array(cv2.convexHull(approx_curve, clockwise=False),
                                 dtype='float32')
        marker_edges1.append(approx_curve)
        marker_edges2.append(sorted_curve)
    return marker_edges1, marker_edges2

def homothetie_marker(img_orig, sorted_curve, marker_size):
    """
    Find the perspective transfomation to get a rectangular 2D marker
    """
    warped_size = marker_size**2
    ideal_corners = np.float32(((0, 0), (warped_size - 1, 0), (warped_size - 1, warped_size - 1),
                                         (0, warped_size - 1)))
    M = cv2.getPerspectiveTransform(sorted_curve, ideal_corners)
    marker2D_img = cv2.warpPerspective(img_orig, M, (warped_size,warped_size))
    return marker2D_img

def get_refs(filepath):
    """
    Collect reference markers matrices -> binary matrices array
    """
    fic = open(filepath, "r")
    _str = fic.read()
    markers_array = json.loads(_str)
    all_markers_array = [[] for j in range(4)]
    for array in markers_array:
        for j in range(4):
            all_markers_array[j].append(array)
            array = np.rot90(np.array(array))
    return np.array(all_markers_array, dtype="float32")

def sort_corners(corners):
    top_corners = sorted(corners, key=lambda x : x[1])
    top = top_corners[:2]
    bot = top_corners[2:]
    if len(top) == 2 and len(bot) == 2:
        tl = top[1] if top[0][0] > top[1][0] else top[0]
        tr = top[0] if top[0][0] > top[1][0] else top[1]
        br = bot[1] if bot[0][0] > bot[1][0] else bot[0]
        bl = bot[0] if bot[0][0] > bot[1][0] else bot[1]
        corners = np.float32([tl, tr, br, bl])
    return corners

def curve_to_quadrangle(points):
    assert points.size == 8, 'not a quadrangle'
    vertices = [p[0] for p in points]
    return np.float32([x for x in vertices])

def get_bit_matrix(img, marker_size):
    """
    split_coeff : découpage de l'image en x*x cases
    cell_size : w, h
    """
    warped_size = marker_size**2
    blur = cv2.GaussianBlur(img.copy(),(5,5),0)
    _, warped_bin = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)
    marker = img.reshape(
        [marker_size, warped_size / marker_size, marker_size, warped_size / marker_size]
    )
    marker = np.median(np.median(marker, axis=3), axis=1)
    marker[marker < 127] = 0
    marker[marker >= 127] = 1
    return marker

def get_bit_matrix2(img, split_coeff):
    """
    split_coeff : découpage de l'image en x*x cases
    cell_size : w, h
    """
    blur = cv2.GaussianBlur(img,(5,5),0)
    _, img = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    assert all(len(row) == len(img) for row in img) #matrice carrée
    cell_size = len(img)/split_coeff, len(img[0])/split_coeff
    bit_matrix = [[0 for x in range(split_coeff)] for y in range(split_coeff)]
    for y in range(split_coeff):
        for x in range(split_coeff):
            cell = img[(x*cell_size[0]):(x+1)*cell_size[0], (y*cell_size[1]):(y+1)*cell_size[1]]
            nb_white = cv2.countNonZero(cell)
            if nb_white > (cell_size[0]**2)/2:
                bit_matrix[x][y] = 1 #is white
    return bit_matrix

def refine_corners(gray, markers_corners):
    precise_corners = []
    for tag_id, corners in markers_corners.items():
        for c in range(4):
            precise_corners.append(corners[c].tolist()[0])
    a = np.float32(precise_corners)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    precise_corners = cv2.cornerSubPix(gray, a, (6,6), (-1,-1), criteria)
    for i, corners in enumerate(markers_corners.values()):
        corners = []
        for c in range(4):
            corners.append(np.array(precise_corners[i*4 + c]))
        corners = np.float32(corners)
    return markers_corners

def estimate(frame, markers):
    for id_, corners in markers.items():
        pts = np.array(corners, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(frame,[np.array([pts[0], pts[1], pts[2], pts[3]])],True,(0,255,255),2)
        cv2.putText(frame, str(id_), (pts[0, 0, 0], pts[0, 0, 1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), thickness=3)
    return frame

def refine_markers(frame, markers):
    assert markers, 'markers is empty'
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners_id, corners_list = [], []
    for id_, points in markers.items():
        corners_list.append(points)
        corners_id.append(id_)
    markers_corners = np.array(corners_list)
    markers_corners = refine_corners(gray, markers_corners)
    markers_  = {}
    for i, index in enumerate(corners_id):
        markers_[index] = markers_corners[i]
    return markers_
