#!/usr/bin/python

import subprocess
import picamera
from SimpleCV import Image, Barcode
import cv2
import time



def findBarCode():

	# capture into stream

	subprocess.call("raspistill -n -w %s -h %s -o tmp.png" % (640, 480), shell=True)

	img = Image("tmp.png")
	img.show()
	time.sleep(3)
	#img=Image(ImageName)
	barcode=img.findBarcode()
	print barcode.data
	#barcode[0].draw(color=(255,0,0), width=1)

findBarCode()


