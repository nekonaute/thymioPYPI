import cv2
import numpy as np 
from matplotlib import pyplot as plt 


def gaussianBlur(image):
	kernel = np.ones((5,5),np.float32)/25
	dst = cv2.filter2D(img,-1,kernel)
	return dst

# anything that has an intensity gradient more than maxVal are definitely edges
# anything that has an intesnity gradient less than minVal are definitely no edges
# those in between are classified as edges or not based on connectivity
def canny(image, minVal, maxVal):
	return cv2.Canny(image, minVal, maxVal)

def convertToBW(image):
	return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def lines(edges):
	return cv2.HoughLines(edges, 1, np.pi/180, 130)

def showlines(img, lines):
	coord=[]
	for rho,theta in lines[0]:
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		x1 = int(x0 + 1000*(-b))
		y1 = int(y0 + 1000*(a))
		x2 = int(x0 - 1000*(-b))
		y2 = int(y0 - 1000*(a))
		c=[x1, y1, x2, y2]
		coord.append(c)
		cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
	showImage(img)

# gets the vectors associated with the lines given from the Hough function
def getVectors(lines):
	coord=[]
	for rho,theta in lines[0]:
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		x1 = int(x0 + 1000*(-b))
		y1 = int(y0 + 1000*(a))
		x2 = int(x0 - 1000*(-b))
		y2 = int(y0 - 1000*(a))
		c=[x1, y1, x2, y2]
		coord.append(c)
	return coord

# vector1 and vector2 are two tables each containing two set of points
def findIntersection(vector1, vector2):
	x1=vector1[0]
	y1=vector1[1]
	x2=vector1[2]
	y2=vector1[3]
	x3=vector2[0]
	y3=vector2[1]
	x4=vector2[2]
	y4=vector2[3]
	d=((float)(x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
	if (d==0):
		return np.array(np.array(np.array(np.array([-1, -1]))))
	intersection_x=((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d
	intersection_y= ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d
	return np.array(np.array(np.array(np.array([intersection_x, intersection_y]))))


#lines : result of Houghlines
def findCorners(lines):
	vectors=getVectors(lines)
	res=len(vectors)*(len(vectors)-1)/2
	#corners=np.zeros((res, 2))
	corners=[]
	k=0
	for i in xrange(len(vectors)):
		for j in xrange(i+1, len(vectors), 1):
			inter=findIntersection(vectors[i], vectors[j])
			#corners[k]=inter
			corners.append(inter)
			#corners=np.concatenate((corners, inter), axis=0)
			#corners.vstack(findIntersection(vectors[i], vectors[j]))
			k+=1
	return corners


def showImage(image):
	cv2.imshow('image',image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def drawPoints2(image, points):
	for point in points:
		print point[0]
		cx, cy=point
		cv2.circle(image,(int(cx),int(cy)),10,(255,255,255),-11)
		cv2.circle(image,(int(cx),int(cy)),11,(0,0,255),1) # draw circle
		cv2.ellipse(image, (int(cx),int(cy)), (10,10), 0, 0, 90,(0,0,255),-1 )
		cv2.ellipse(image, (int(cx),int(cy)), (10,10), 0, 180, 270,(0,0,255),-1 )
		cv2.circle(image,(int(cx),int(cy)),1,(0,255,0),1) # draw center
		#cv2.putText(image,(int(cx)+10,int(cy)-10),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,180,180))
	showImage(image)

def drawPoints(image, points):
	print points
	showImage(image)
	for point in points:
		print "point : ", point
		cx, cy=point[0]
		cv2.circle(image,(int(cx),int(cy)),5,(255,0,0),-1)
	return image

"""
# example of gaussian blur : 
img=cv2.imread('rect.png')
img2=convertToBW(img)
showImage(img2)
img=gaussianBlur(img)
showImage(img)
# example of canny edge detection
minVal=50
maxVal=150
img=canny(img, minVal, maxVal)
showImage(img)

houghlines=lines(img)
#img=cv2.imread('rect.png')
img=cv2.imread('rect.png')
showlines(img, houghlines)
"""

img=cv2.imread('rect.png')
img=gaussianBlur(img)
minVal=50
maxVal=150
img=canny(img, minVal, maxVal)
houghlines=lines(img)
print len(houghlines[0])
print "vectors : \n", getVectors(houghlines)
corners=findCorners(houghlines)
print "nb corners : ", len(corners)
image23=cv2.imread('rect.png')
img=drawPoints(image23, corners)
showlines(img, houghlines)


print "---------------------> ", cv2.arcLength(corners, True)*0.02

res=cv2.approxPolyDP(corners, cv2.arcLength(corners, True)*0.02,True)
print len(res)