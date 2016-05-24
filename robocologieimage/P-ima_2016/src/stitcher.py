#! /usr/bin/env python

import numpy as np
import cv2
import time
print(cv2.ocl.useOpenCL())
cv2.ocl.setUseOpenCL(True)
print(cv2.ocl.useOpenCL())
imgs = []

for f in ('..\data\images\grand_canyon_left_01.png'):
	im = cv2.imread(f)
	imgs.append(im)


for i in imgs:
	cv2.imshow('image',i)
	cv2.waitKey(0)


st=cv2.createStitcher(False)
ret,pano = st.stitch(imgs)

print 'ret',ret

if ret: cv2.imwrite('pano.png',pano)

#cv2.imshow('image',pano)
#cv2.waitKey(2000)

#cv2.destroyAllWindows()
