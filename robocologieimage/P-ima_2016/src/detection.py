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
    def __init__(self, refs, classifier=None):
        self.refs = refs

        # Detection log
        self.nb_tags = 0 # marker nb
        self.nb_quads = 0 # quadrangle nb

        # Different images
        self.frame = None
        self.canny_mat = None
        self.edge_mat = None
        self.markers_mat = None

        # State
        self.online = True

        # Variables
        self.markers_dict = {}
        self.positions = {}
        self.current_tags = []
        self.trajectory = {}
        self.detect_time = {}
        self.homothetie_markers = {}
        self.positionsHistory = []

        # SVM/NeuralNetwork
        self.method = [{"quads":.0, "detected":.0, "success":.0, "error":.0, "non-tag":.0} for _ in range(2)]
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.images_stock = {}
        self.classifier = classifier

    def getImage(self, image_type):
        if image_type == "markers":
            return self.markers_mat
        elif image_type == "edges":
            return self.edge_mat
        elif image_type == "canny":
            return self.canny_mat
        elif image_type == "path":
            return self.path_mat
        elif image_type == "original":
            return self.frame

    def intensity_detection(self, marker, image):
        tag_id = -1
        if any(marker[crd[0], crd[1]] != 0.0 for crd in BORDERS):
            return -1, image
        elif np.all(marker == 0.0):
            return -1, image
        rot_image = image.copy()
        for j in range(4):
            try:
                tag_id = self.refs[j].tolist().index(marker.tolist())
            except ValueError:
                rot_image = np.rot90(rot_image)
                #marker = get_bit_matrix(rot_image, MARKER_SIZE)
            else:
                return tag_id, rot_image
        return -1, image

    def classifier_detection(self, image):
        rot_image = image.copy()
        for rot90 in range(4):
            data = rot_image.reshape((1, -1))
            probas = self.classifier.predict_proba(data)
            if np.max(probas) < 0.70:
                rot_image = np.rot90(rot_image)
                continue
            tag_id = self.classifier.predict(data)[0]
            return tag_id, rot_image
        return -1, image

    def detect(self, mat_g, pos, approx):
        selected = {}
        nb_detected = 1e-6
        nb_success = 1e-6
        nb_error = 1e-6
        nb_nontag = 1e-6
        nb_doublon = 1e-6
        for i in range(len(pos)):
            results = []
            corners = curve_to_quadrangle(pos[i])
            image = homothetie_marker(mat_g, corners, MARKER_SIZE)

            # Normalisation
            image = (image-np.mean(image))/np.std(image)

            # # Methode 1
            marker = get_bit_matrix(image, MARKER_SIZE)
            tag_id, rot_image = self.intensity_detection(marker, image)

            # # Méthode 2
            # if self.classifier:
            #     tag_id2, rot_image2 = self.classifier_detection(image)

            # Register only tags where all methods succeeds
            # Evaluation & Collect data to feed my learning algorithm
            if tag_id != -1:
                nb_detected += 1
                if tag_id in self.valid_ids:
                    nb_success += 1
                else:
                    nb_error += 1
                if tag_id in selected.keys():
                    nb_doublon += 1
                else:
                    selected[tag_id] = approx[i]
                    self.homothetie_markers[tag_id] = rot_image*255
                if self.images_stock.get(tag_id, False) is False:
                    self.images_stock[tag_id] = []
                self.images_stock[tag_id].append(rot_image)
            else:
                nb_nontag += 1
                if self.images_stock.get(-1, False) is False:
                    self.images_stock[-1] = []
                self.images_stock[-1].append(rot_image)

        self.nb_selected = len(selected)
        self.nb_quads = len(pos)
        self.nb_detected = nb_detected
        self.nb_success = nb_success
        self.nb_error = nb_error
        self.nb_nontag = nb_nontag
        self.nb_doublon = nb_doublon
        self.detected = selected.keys()
        return selected


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

    def normalize_position(self, positions, w, h):
        normalized = {}
        for id_ in positions:
            normalized[id_] = np.float64(positions[id_].copy())
            normalized[id_][0][0] = float(positions[id_][0][0]) / float(w)
            normalized[id_][0][1] = float(positions[id_][0][1]) / float(h)
        return normalized

    def update(self, frame, parameters, seconds):
        self.markers_dict = {}
        self.valid_ids = parameters["existing_tags"].replace("[","").replace("]","").replace(","," ").split()
        self.valid_ids = map(int, self.valid_ids)
        self.previous_tags = self.current_tags[:]
        #self.fgmask = self.backgroundSubtractor(frame)
        self.frame = np.copy(frame)
        h, w, _ = frame.shape
        mat_g = rgb2gray(frame)
        self.canny_mat = canny_algorithm(mat_g, parameters['kernel'],
                                        parameters['sigma'])
        approx, sort = find_contours(self.canny_mat.copy(),
                                        parameters['min_contour_area'],
                                        parameters['max_contour_area'],
                                        parameters['eps'],
                                        parameters['min_dist'],
                                        parameters['max_dist'])
        zeros = np.zeros((h, w, 3), np.uint8)
        self.edge_mat = cv2.drawContours(zeros, approx, -1, (255,255,255), 1)
        raw_markers = self.detect(mat_g, sort, approx)
        if raw_markers:
            self.markers_dict = raw_markers
            self.markers_mat = estimate(frame, self.markers_dict)
        else:
            self.markers_mat = frame
        curr_positions = self.update_positions(self.positions,self.markers_dict)
        self.normalized_positions = self.normalize_position(curr_positions, w, h)
        self.trajectory, self.path_ima = self.update_trajectory(frame.copy(), self.trajectory, self.positions, curr_positions)
        self.detect_time = self.updateDetectTime(self.detect_time, self.markers_dict.keys(), seconds)
        self.current_tags = self.markers_dict.keys()
        self.positions = curr_positions
        self.positionsHistory.append(self.normalized_positions)
