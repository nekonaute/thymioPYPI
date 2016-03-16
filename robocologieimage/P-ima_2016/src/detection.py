 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from utilities import *
import interface as ui
import cv2
import numpy as np

# BORDERS = [
# [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [1, 0], [1, 5], [2, 0], [2, 5], [3, 0],
# [3, 5], [4, 0], [4, 5], [5, 0], [5, 5], [5, 0], [5, 1], [5, 2], [5, 3], [5, 4]
# ]
# MARKER_SIZE = 6

BORDERS = [
[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, 0], [1, 4], [2, 0], [2, 4], [3, 0],
[3, 4], [4, 0], [4, 4], [4, 0], [4, 1], [4, 2], [4, 3]
]
MARKER_SIZE = 5

class Detector(object):
    def __init__(self, refs):
        self.refs = refs
        self.curr_mk = 0 # marker nb
        self.curr_qr = 0 # quadrangle nb
        self.frame = None
        self.canny_mat = None
        self.edge_mat = None
        self.markers_ima = None
        self.markers_dict = {}
        self.positions = {}
        self.trajectory = {}
        self.detect_time = {}
        self.homothetie_markers = {}
        self.method1 = 0
        self.method2 = 0

    def get(self, info):
        return {'edges' : self.edge_mat,
        'canny' : self.canny_mat,
        'markers': self.markers_ima,
        'path': self.path_ima,
        'original' : self.frame}[info]


    def _detect(self, marker):
        id_ = None
        if any(marker[crd[0], crd[1]] != 0.0 for crd in BORDERS):
            return False, None
        elif np.all(marker == 0.0):
            return False, None
        for j in range(4):
            try:
                id_ = self.refs[j].tolist().index(marker.tolist())
            except ValueError:
                pass
            else:
                return True, id_
        return False, None


    def detect(self, mat_g, pos, approx):
        detected = {}
        for i in range(len(pos)):
            sorted_curve = pos[i]
            corners = curve_to_quadrangle(pos[i])
            image = homothetie_marker(mat_g, corners, MARKER_SIZE)
            # Methode 1
            marker = get_bit_matrix(image, MARKER_SIZE)
            success, id_ = self._detect(marker)
            if success:
                self.method1 += 1
                detected[id_] = approx[i]
                self.homothetie_markers[id_] = image
                continue

            # Methode 2
            marker = np.float32(get_bit_matrix2(image, MARKER_SIZE))
            success, id_ = self._detect(marker)
            if success:
                self.method2 += 1
                detected[id_] = approx[i]
                self.homothetie_markers[id_] = image
                continue

        #print self.method1, self.method2, self.method1/float((self.method1+self.method2)), self.method2/float((self.method1+self.method2))
        self.curr_mk = len(detected)
        self.curr_qr = len(pos)
        self.detected = detected.keys()
        return detected

    def update_positions(self, positions, markers):
        positions = {}
        for id_, corners in markers.items():
            pts = np.array(corners, np.int32)
            pts = pts.reshape((-1,1,2))
            positions[id_] = (pts[0] + pts[3])/2
        return positions

    def update_trajectory(self, frame, trajectory, prev_positions, curr_positions):
        for id_, corners in curr_positions.items():
            if not id_ in trajectory.keys():
                trajectory[id_] = []

        for id_, corners in trajectory.items():
            if len(trajectory[id_]) > 500:
                trajectory[id_] = trajectory[id_][-10:-1]
            if id_ in prev_positions.keys() and id_ in curr_positions.keys():
                p, c = prev_positions[id_][0], curr_positions[id_][0]
                if not (p[0]-5 < c[0] < p[0]+5 and p[1]-5 < c[1] < p[1]+5):
                    trajectory[id_].append(p)
                    trajectory[id_].append(c)
                cv2.polylines(frame, [np.array(trajectory[id_])], False,(0,255,0),3,cv2.LINE_AA)
            elif id_ in curr_positions.keys():
                c = curr_positions[id_][0]
                if trajectory[id_]:
                    p = trajectory[id_][-1]
                    if not (p[0]-5 < c[0] < p[0]+5 and p[1]-5 < c[1] < p[1]+5):
                        trajectory[id_].append(c)
                else:
                    trajectory[id_].append(c)
                cv2.polylines(frame, [np.array(trajectory[id_])], False,(255,0,0),1,cv2.LINE_AA)
            else:
                cv2.polylines(frame, [np.array(trajectory[id_])], False,(255,255,0),1,cv2.LINE_AA)
        return trajectory, frame

    def updateDetectTime(self, detect_time, curr_markers, seconds):
        for id_ in curr_markers:
            if not id_ in detect_time.keys():
                detect_time[id_] = 0
            else:
                detect_time[id_] += seconds
        return detect_time


    def update(self, frame, seconds):
        self.frame = np.copy(frame)
        h, w, _ = frame.shape
        mat_g = rgb2gray(frame)
        self.canny_mat = canny_algorithm(mat_g)
        approx, sort = find_contours(self.canny_mat.copy())
        zeros = np.zeros((h, w, 3), np.uint8)
        self.edge_mat = cv2.drawContours(zeros, approx, -1, (255,255,255), 1)
        raw_markers = self.detect(mat_g, sort, approx)
        if raw_markers:
            self.markers_dict = raw_markers
            self.markers_ima = estimate(frame, self.markers_dict)
        else:
            self.markers_ima = frame
        positions = self.update_positions(self.positions,self.markers_dict)
        self.trajectory, self.path_ima = self.update_trajectory(frame.copy(), self.trajectory, self.positions, positions)
        self.detect_time = self.updateDetectTime(self.detect_time, self.markers_dict.keys(), seconds)
        self.positions = positions
