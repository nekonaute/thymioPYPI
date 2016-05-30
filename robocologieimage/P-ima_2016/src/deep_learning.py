from __future__ import print_function


# Authors: Yann N. Dauphin, Vlad Niculae, Gabriel Synnaeve
# License: BSD

# Edited by Elias Rhouzlane for Tag Prediction
# UPMC - PIMA

import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import convolve
from sklearn import linear_model, datasets, metrics
from sklearn.cross_validation import train_test_split
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

from main import NPZ_DATA, CLF_NAMEFILE

###############################################################################
# Setting up

def nudge_dataset(X, Y):
    """
    This produces a dataset 5 times bigger than the original one,
    by moving the 25x25 images in X around by 1px to left, right, down, up
    """

    direction_vectors = [
        [[0, 1, 0],
         [0, 0, 0],
         [0, 0, 0]],

        [[0, 0, 0],
         [1, 0, 0],
         [0, 0, 0]],

        [[0, 0, 0],
         [0, 0, 1],
         [0, 0, 0]],

        [[0, 0, 0],
         [0, 0, 0],
         [0, 1, 0]]]


    shift = lambda x, w: convolve(x.reshape((25,25)), mode='constant',
                                  weights=w).ravel()
    X = np.concatenate([X] +
                       [np.apply_along_axis(shift, 1, X, vector)
                        for vector in direction_vectors])
    Y = np.concatenate([Y for _ in range(5)], axis=0)

    return X, Y

# Load Data
class Dataset(object): pass

# The digits dataset
npzfile = np.load("../data/npz/{}.npz".format(NPZ_DATA))
digits = Dataset()
digits.target = npzfile['arr_0']
digits.images = npzfile['arr_1']

# Format
X = np.empty((len(digits.images),25,25))
for i in range(len(digits.images)):
    X[i] = digits.images[i]
    
# To apply a classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(X)
X = X.reshape((n_samples, -1))
X = np.asarray(X, 'float32')

#print(type(digits.images))
Y = digits.target
print("Start Producing Data.")
#X, Y = nudge_dataset(X, digits.target)
X[X > 1.0] = 1.0
X[X < 0.0] = 0.0
X_train, X_test, Y_train, Y_test = train_test_split(X, Y,
                                                    test_size=0.33, random_state=42)

# The data that we are interested in is made of 8x8 images of digits, let's
# have a look at the first 3 images, stored in the `images` attribute of the
# dataset.  If we were working from image files, we could load them using
# pylab.imread.  Note that each image must have the same size. For these
# images, we know which digit they represent: it is given in the 'target' of
# the dataset.
images_and_labels = list(zip(X_train, Y_train))
for index, (image, label) in enumerate(images_and_labels[:20]):
    plt.subplot(2, 20, index + 1)
    plt.axis('off')
    plt.imshow(image.reshape((25, 25)), cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('%i' % label)

# Models we will use
logistic = linear_model.LogisticRegression()

rbm = BernoulliRBM(random_state=0, verbose=3)

classifier = Pipeline(steps=[('rbm', rbm), ('logistic', logistic)])

###############################################################################
# Training
# Hyper-parameters. These were set by cross-validation,
# using a GridSearchCV. Here we are not performing cross-validation to
# save time.
rbm.learning_rate = 0.06
rbm.n_iter = 10
# More components tend to give better prediction performance, but larger
# fitting time
rbm.n_components = 500
logistic.C = 6000.0

# Training RBM-Logistic Pipeline
print("Start Training (RBM-Logistic)")
classifier.fit(X_train, Y_train)

# Training Logistic regression
# print("Start Training (Logistic)")
# logistic_classifier = linear_model.LogisticRegression(C=100.0, verbose=3)
# logistic_classifier.fit(X_train, Y_train)

###############################################################################
# Evaluation

predicted = classifier.predict(X_test)
print()
print("Logistic regression using RBM features:\n%s\n" % (
    metrics.classification_report(
        Y_test,
        predicted)))

# print("Logistic regression using raw pixel features:\n%s\n" % (
#     metrics.classification_report(
#         Y_test,
#         logistic_classifier.predict(X_test))))
###############################################################################
# Save

joblib.dump(classifier, '../data/classifier/deep/{}'.format(CLF_NAMEFILE))

###############################################################################
# Plotting
images_and_predictions = list(zip(X_test, predicted))
for index, (image, prediction) in enumerate(images_and_predictions[:20]):
    plt.subplot(2, 20, index + 21)
    plt.axis('off')
    plt.imshow(image.reshape((25, 25)), cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('%i' % prediction)

plt.show()

# plt.figure(figsize=(4.2, 4))
# for i, comp in enumerate(rbm.components_[:10]):
#     plt.subplot(10, 10, i + 1)
#     plt.imshow(comp.reshape((25,25)), cmap=plt.cm.gray_r,
#                interpolation='nearest')
#     plt.xticks(())
#     plt.yticks(())
# plt.suptitle('100 components extracted by RBM', fontsize=16)
# plt.subplots_adjust(0.08, 0.02, 0.92, 0.85, 0.08, 0.23)
#
# plt.show()
