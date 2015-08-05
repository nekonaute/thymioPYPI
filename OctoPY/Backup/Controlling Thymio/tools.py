

import numpy as np
import cv2
import imutils



# image img is already resized
# k : number of biggest contours we keep
def find_squares(img, k=20):

    # converting image to grayscale, blurring and finding edges
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray=cv2.bilateralFilter(gray, 11, 17, 17)
    edged=cv2.Canny(gray, 30, 200)

    # find contours in the edged image and sorting them by size
    # here we keep the k biggest contours
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:k]
    screenCnt = None

    squares=[]
    positions=[]
    # loop over our contours
    for c in cnts:
    	# approximate the contour
    	peri = cv2.arcLength(c, True)
    	# here we use 2% of the perimeter of the contour
    	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    	# if our approximated contour has four points, then
    	# we can assume that we have found our objectif
    	if len(approx) == 4:
    		squares.append(approx)
    		coordinates=cv2.moments(c)
		if coordinates['m00']==0:
			continue
    	X = int(coordinates['m10']/coordinates['m00'])
    	Y = int(coordinates['m01']/coordinates['m00'])
    	positions.append([X,Y])

    #print len(squares)
    # draw the contours : 
    #for square in squares:
    """
    cv2.drawContours(img, squares, -1, (0, 255, 0), 3)
    cv2.imshow("squares", img)
    cv2.waitKey(0)
    """
    return squares, positions


# contour is a set of points
# function returns the four corners in order : 
# topleft, topright, bottomright, bottomleft
def orderPointsRect(contour):
	# to make it easier to deal with
	points=contour.reshape(4, 2)
	# rect will hold the four corners of the contour
	rect=np.zeros((4,2), dtype="float32")
	s=points.sum(axis=1)
	rect[0]=points[np.argmin(s)]
	rect[2]=points[np.argmax(s)]
	diff=np.diff(points, axis=1)
	rect[1]=points[np.argmin(diff)]
	rect[3]=points[np.argmax(diff)]
	return rect

# returns the distance from point A to point B
def distance(A, B):
	return np.sqrt(((A[0] - B[0]) ** 2) + ((A[1] - B[1]) ** 2))


# returns true if the ratio between width and height is bigger or equal to epsilon
# epsilon is between 0 and 1
# the smaller epsilon is, the easier a rectangle is a square
def isSquare(width, height, epsilon):
	L=max(width, height)
	l=float(min(width, height))
	return l/L>=epsilon

# takes a rectangular contour as an agrument
def getContourImage(square, img):
	rect=orderPointsRect(square)
	ratio=img.shape[0]/taille

	rect*=ratio

	# now that we have our rectangle of points, let's compute
	# the width of our new image
	(tl, tr, br, bl) = rect
	width1 = distance(br, bl)
	width2 = distance(tr, tl)
	 
	# ...and now for the height of our new image
	height1=distance(tr, br)
	height2=distance(tl, bl)
	 
	# take the maximum of the width and height values to reach
	# our final dimensions
	maxWidth = max(int(width1), int(width2))
	maxHeight = max(int(height1), int(height2))



	# check if the rectangle is a square
	epsilon=50
	if not isSquare(maxWidth, maxHeight, epsilon):
		print "Region is not a square"
		print "width : ", maxWidth
		print "height : ", maxHeight
		return np.array([False]), -1, -1

	# construct our destination points which will be used to
	# map the screen to a top-down, "birds eye" view
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# calculate the perspective transform matrix and warp
	# the perspective to grab the screen
	M = cv2.getPerspectiveTransform(rect, dst)
	warp = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

	# show the image
	#cv2.imshow("warp", imutils.resize(warp, height=int(taille)))
	#cv2.waitKey(1000)


	# return the new image (close up of the square) and the square's dimensions in the original image
	return imutils.resize(warp, height=int(taille)), maxWidth/ratio, maxWidth/ratio

# corner : number from 1 to 4
# 1 : top left
# 2 : top right
# 3 : bottom right
# 4 : bottom left
def getCorner(corner, img):
	h, w = img.shape[0:2]
	dX, dY=(int(w*0.5), int(h*0.5))
	if (corner==1):
		crop=img[0:dY, 0:dX]
		return imutils.resize(crop, height=int(taille))
	if (corner==2):
		crop=img[0:dY, dX:w]
		return imutils.resize(crop, height=int(taille))
	if (corner==3):
		crop=img[dY:h, dX:w]
		return imutils.resize(crop, height=int(taille))
	if (corner==4):
		crop=img[dY:h, 0:dX]
		return imutils.resize(crop, height=int(taille))
	print "error, invalid corner (must be an integer from 1-4"
	return -1


def Histogram(img):
	image_HSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	return cv2.calcHist([image_HSV], [0], None, [180], [0,180])

# calculates the center of the corner of the square dimensioned width*height 
# positioned at position in the original photo
def calculateCenter(position, width, height, corner):
	x=position[0]
	y=position[1]
	if corner==1:
		# top left
		centreX=x-width/4.0
		centreY=y-height/4.0
	if corner==2:
		# top right
		centreX=x+width/4.0
		centreY=y-height/4.0
	if corner==3:
		# bottom right
		centreX=x+width/4.0
		centreY=y+height/4.0
	if corner==4 : 
		centreX=x-width/4.0
		centreY=y+height/4.0
	return [int(centreX), int(centreY)]

# color is a number between 1 and 3
# 1 : RED
# 2 : BLUE
# 3 : GREEN

# corner is a number between 1 and 4
# 1 : top left square
# 2 : top right square
# 3 : bottom right square
# 4 : bottom left square

# if there exists a square with the color "color" in the sub-square "corner"
# return "LEFT" or "RIGHT"
# if no such color exists, return -1


def drawCross(img, x, y):
	img[y][x]=[0, 255, 0]
	img[y+1][x]=[0, 255, 0]
	img[y-1][x]=[0, 255, 0]
	img[y][x+1]=[0, 255, 0]
	img[y][x-1]=[0, 255, 0]












