 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from utilities import *
import interface as ui
import cv2
import numpy as np

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics

BORDERS = [
[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, 0], [1, 4], [2, 0], [2, 4], [3, 0],
[3, 4], [4, 0], [4, 4], [4, 0], [4, 1], [4, 2], [4, 3]
]
MARKER_SIZE = 5

class Detector(object):
    def __init__(self, refs, classifier=None, valid_ids=[]):
        self.refs = refs
        self.valid_ids = valid_ids
        self.curr_mk = 0 # marker nb
        self.curr_qr = 0 # quadrangle nb
        self.frame = None
        self.canny_mat = None
        self.edge_mat = None
        self.markers_ima = None
        self.fgmask = None
        self.markers_dict = {}
        self.positions = {}
        self.trajectory = {}
        self.detect_time = {}
        self.homothetie_markers = {}
        self.method = [{"detected":.0, "success":.0, "error":.0, "unsure":.0} for _ in range(2)]
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.images_stock = {}
        self.clf = classifier

    def get(self, info):
        return {'edges' : self.edge_mat,
        'canny' : self.canny_mat,
        'markers': self.markers_ima,
        'path': self.path_ima,
        'original' : self.frame,
        'fgmask' : self.fgmask}[info]


    def _detect(self, marker):
        id_ = None
        if any(marker[crd[0], crd[1]] != 0.0 for crd in BORDERS):
            return False, None, None
        elif np.all(marker == 0.0):
            return False, None, None
        for j in range(4):
            try:
                id_ = self.refs[j].tolist().index(marker.tolist())
            except ValueError:
                pass
            else:
                return True, j, id_
        return False, None, None


    def detect(self, mat_g, pos, approx):
        detected = {}
        id_M1, id_SVM = None, None
        success1, success2 = False, False
        for i in range(len(pos)):
            sorted_curve = pos[i]
            corners = curve_to_quadrangle(pos[i])
            image = homothetie_marker(mat_g, corners, MARKER_SIZE)

            # Normalisation
            image = (image-np.mean(image))/np.std(image)

            # Methode 1
            marker = get_bit_matrix(image, MARKER_SIZE)
            success1, j, id_M1 = self._detect(marker)
            if success1:
                self.method[0]['detected'] += 1
                if id_M1 not in self.valid_ids:
                    self.method[0]['error'] += 1
                else:
                    self.method[0]['success'] += 1
                detected[id_M1] = approx[i]
                image_ = image.copy()
                if j == 1:
                    j = 3
                elif j == 3:
                    j = 1
                for k in range(j):
                    image_ = np.rot90(image_.copy())
                self.homothetie_markers[id_M1] = image_*255


            # Méthode 3 par Apprentissage
            if self.clf and not success1:
                image_ = image.copy()
                for j_ in range(4):
                    data = image_.reshape((1, -1))
                    probas = self.clf.predict_proba(data)
                    if np.max(probas) > 0.85:
                        self.method[1]['detected'] += 1
                        id_SVM = self.clf.predict(data)[0]
                        if id_SVM not in self.valid_ids or (success1 and id_M1 != id_SVM and id_M1 in self.valid_ids):
                            self.method[1]['error'] += 1
                        elif success1 and id_M1 == id_SVM and id_M1 in self.valid_ids:
                            self.method[1]['success'] += 1
                        else:
                            self.method[1]['unsure'] += 1
                        success2 = True
                        detected[id_SVM] = approx[i]
                        self.homothetie_markers[id_SVM] = image_*255
                        break
                    else:
                        image_ = np.rot90(image_)

            # Get data to fit my learning algorithm
            if success1 and id_M1 in self.valid_ids:
                if self.images_stock.get(id_M1, False) is False:
                    self.images_stock[id_M1] = []
                image_ = image.copy()
                if j == 1:
                    j = 3
                elif j == 3:
                    j = 1
                for k in range(j):
                    image_ = np.rot90(image_.copy())
                self.images_stock[id_M1].append(image_)
            # elif success2 and id_SVM in self.valid_ids:
            #     if self.images_stock.get(id_SVM, False) is False:
            #         self.images_stock[id_SVM] = []
            #     self.images_stock[id_SVM].append(image_)

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

    def backgroundSubtractor(self, frame):
        fgmask = self.fgbg.apply(frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
        fgmask = cv2.medianBlur(cv2.medianBlur(fgmask, 3),7)
        fgmask[fgmask > 230] = 255
        fgmask[fgmask <= 230] = 0
        return fgmask

    def update(self, frame, seconds):
        #self.fgmask = self.backgroundSubtractor(frame)
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
