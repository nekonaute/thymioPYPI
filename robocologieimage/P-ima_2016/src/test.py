from main import NPZ_DATA, CLF_NAMEFILE

import numpy as np

# Standard scientific Python imports
import matplotlib.pyplot as plt

# Import datasets, classifiers and performance metrics
from sklearn import datasets, svm, metrics
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from sklearn.grid_search import GridSearchCV

class Dataset(object):
    pass

# The digits dataset
npzfile = np.load("../data/npz/{}.npz".format(NPZ_DATA))
digits = Dataset()
digits.target = npzfile['arr_0']
digits.images = np.array([_[0] for _ in npzfile['arr_1']])

print digits.target.shape

# Split into a training set and a test set using a stratified k fold
X_train, X_test, y_train, y_test = train_test_split(digits.images, digits.target, test_size=0.33, random_state=42)

# The data that we are interested in is made of 8x8 images of digits, let's
# have a look at the first 3 images, stored in the `images` attribute of the
# dataset.  If we were working from image files, we could load them using
# pylab.imread.  Note that each image must have the same size. For these
# images, we know which digit they represent: it is given in the 'target' of
# the dataset.
images_and_labels = list(zip(X_train, y_train))
for index, (image, label) in enumerate(images_and_labels[:40]):
    plt.subplot(2, 40, index + 1)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('%i' % label)

# To apply a classifier on this data, we need to flatten the image, to
# turn the data in a (samples, feature) matrix:
n_samples = len(X_train)
data_train = X_train.reshape((n_samples, -1))

# C_range = np.logspace(-2, 10, 13)
# gamma_range = np.logspace(-9, 3, 13)
# param_grid = dict(gamma=gamma_range, C=C_range)
# cv = StratifiedShuffleSplit(y_train, n_iter=5, test_size=0.2, random_state=42)
# classifier = GridSearchCV(svm.SVC(C=1, probability=True), param_grid=param_grid, cv=cv, verbose=3)

tuned_parameters = [
  {'C': [1], 'kernel': ['linear']},
 ]

# Grid Search Algorithm (5) - Create a classifier: a support vector classifier
classifier = GridSearchCV(svm.SVC(C=1, probability=True), tuned_parameters, cv=5, verbose=3)

# We learn the digits on the first half of the digits
classifier.fit(data_train, y_train)

# Now predict the value of the digit on the second half:
expected = y_test
#print data[n_samples / 2:].shape
predicted = classifier.predict(X_test.reshape((len(X_test), -1)))
joblib.dump(classifier, '../data/classifier/{}'.format(CLF_NAMEFILE))
print("Classification report for classifier %s:\n%s\n"      % (classifier, metrics.classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))

images_and_predictions = list(zip(X_test, predicted))
for index, (image, prediction) in enumerate(images_and_predictions[:40]):
    plt.subplot(2, 40, index + 41)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('%i' % prediction)

plt.show()
