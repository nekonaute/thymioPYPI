#!/usr/bin/env python

import os
import re
import argparse
from datetime import datetime
import math
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np


CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

# SEABORN
sns.set()
sns.set_style('white')
sns.set_context('paper')
palette = sns.color_palette("husl", 3)


# GRAPHS GLOBAL VARIABLES
linewidth = 2
linestyles = ['-', '--', '-.']
linestylesOff = ['-', '-', '-']
markers = [None, None, None] #['o', '+', '*']

dpi = 96
size = (1280/dpi, 1024/dpi)



def main(args) :
	regexp = re.compile(r" (\d+):(\d+):(\d+).*DEBUG: Value : (\d+)")

	if os.path.isfile(args.file) :
		with open(args.file, 'r') as fileRead :
			fileRead = fileRead.readlines()

			lastDate = None
			listValues = []
			durationSeconds = 0
			histTime = {}
			listTimes = []
			for line in fileRead :
				s = regexp.search(line.rstrip('\n'))

				# print(line)
				if s :
					hour = int(s.group(1))
					minutes = int(s.group(2))
					seconds = int(s.group(3))

					value = int(s.group(4))
					listValues.append(value)

					curDate = datetime.strptime(str(hour) + ":" + str(minutes) + ":" + str(seconds), "%H:%M:%S")

					if lastDate == None :
						lastDate = curDate
					else :
						durationSeconds += (curDate - lastDate).seconds

					if durationSeconds not in histTime :
						histTime[durationSeconds] = 0
						listTimes.append(durationSeconds)

					histTime[durationSeconds] += 1

					lastDate = curDate


			# -- Number of wall/robot
			listTypes = [0, 0, 0, 0, 0, 0]
			# -- Size of barcode
			listSizesRobot = [0, 0, 0, 0, 0]
			listSizesWall = [0, 0, 0, 0, 0]
			# -- Height number
			listHeightRobot = [0, 0, 0, 0, 0]
			listHeightWall = [0, 0, 0, 0, 0]

			cpt = 0
			while cpt < len(listValues) :
				value = listValues[cpt]
				cent = int(math.floor(value/100))
				# print(cent)
				listTypes[cent] += 1

				value = value - cent*100

				dec = int(math.floor(value/10))
				value = int(value - dec*10)

				if cent == 5 :
					listSizesRobot[dec] += 1
					listHeightRobot[value] += 1
				else :
					listSizesWall[cent] += 1
					listHeightWall[value] += 1

				cpt += 1

			print("Number of scanning : " + str(len(listValues)))


			# MATPLOTLIB PARAMS
			matplotlib.rcParams['font.size'] = 15
			matplotlib.rcParams['font.weight'] = 'bold'
			matplotlib.rcParams['axes.labelsize'] = 15
			matplotlib.rcParams['axes.titlesize'] = 15
			matplotlib.rcParams['axes.labelweight'] = 'bold'
			matplotlib.rcParams['xtick.labelsize'] = 15
			matplotlib.rcParams['ytick.labelsize'] = 15
			matplotlib.rcParams['legend.fontsize'] = 15

			fig, (ax0, ax1, ax2) = plt.subplots(ncols = 3, figsize = size)


			# Histogram of times
			listTimes.sort()

			tabHistTimeSeconds = []
			for time in range(listTimes[-1]) :
				if time in histTime :
					tabHistTimeSeconds.append(histTime[time])
				else :
					tabHistTimeSeconds.append(0)

			listTimesMinutes = []
			tabHistTimeMinutes = []
			for time in range(listTimes[-1]) :
				minute = int(math.floor(time/60))

				if minute not in listTimesMinutes :
					listTimesMinutes.append(minute)
					tabHistTimeMinutes.append(0)


				tabHistTimeMinutes[minute] += tabHistTimeSeconds[time]

			listTimesMinutes.sort()

			# print(listTimes)
			# print(histTime)
			# print(tabHistTime)
			width = 0.5
			bars = ax0.bar(listTimesMinutes, tabHistTimeMinutes, width = width, color = 'green')
			# ax0.hist(listSizes, num_bins, facecolor='green', alpha=0.5)
			# ax0.set_xlim(0.0, 1.0)
			# ax0.set_ylim(0.0, mu)
			ax0.set_xlim(0, 30)
			ax0.set_xticks([minute for minute in range(0, listTimesMinutes[-1], 10)])
			ax0.set_xticklabels([minute for minute in range(0, listTimesMinutes[-1], 10)])
			ax0.set_xlabel('Time (minutes)')
			ax0.set_ylabel('Number')
			ax0.set_title('Histogram of scans')


			# Size of barcode
			width = 1
			bars = ax1.bar(range(len(listSizesWall)), listSizesWall, width = width, color = 'green')
			# ax1.hist(listSizes, num_bins, facecolor='green', alpha=0.5)
			# ax1.set_xlim(0.0, 1.0)
			# ax1.set_ylim(0.0, mu)
			ax1.set_xlim(1, 5)
			ax1.set_xticks(range(1, len(listSizesWall)))
			ax1.set_xticklabels(range(1, len(listSizesWall)))
			ax1.set_xlabel('Size')
			ax1.set_ylabel('Number')
			ax1.set_title('Size of barcodes scanned')


			# Height of barcode
			width = 1
			bars = ax2.bar(range(len(listHeightWall)), listHeightWall, width = width, color = 'green')
			# ax2.hist(listHeight, num_bins, facecolor='green', alpha=0.5)
			# ax2.set_xlim(0.0, 1.0)
			# ax2.set_ylim(0.0, mu)
			ax2.set_xlim(1, 5)
			ax2.set_xticks(range(1, len(listHeightWall)))
			ax2.set_xticklabels(range(1, len(listHeightWall)))
			ax2.set_xlabel('Height')
			ax2.set_ylabel('Number')
			ax2.set_title('Height of barcodes scanned')

			fileName = os.path.splitext(os.path.basename(args.file))[0] + "Wall"
			plt.tight_layout()
			plt.savefig(os.path.join(CURRENT_FILE_PATH, fileName + ".png"), bbox_inches = 'tight')
			# plt.savefig(os.path.join(outputDir, "graphs" + str(numDir) + ".png"), bbox_inches = 'tight')
			# plt.show()
			plt.close()

			if args.two :
				fig, (ax0, ax1, ax2) = plt.subplots(ncols=3, figsize = size)

				# Number of wall/robot
				width = 1
				bars = ax0.bar(range(len(listTypes)), listTypes, width = width, color = 'green')
				# ax0.hist(listTypes, num_bins, facecolor='green', alpha=0.5)
				# ax0.set_ylim(0.0, mu)
				ax0.set_xlim(1, 6)
				ax0.set_xticks(range(1, len(listTypes)))
				ax0.set_xticklabels(range(1, len(listTypes)))
				ax0.set_xlabel('Id')
				ax0.set_ylabel('Number')
				ax0.set_title('Number of wall/robot scanned')

				# Size of barcode
				width = 1
				bars = ax1.bar(range(len(listSizesRobot)), listSizesRobot, width = width, color = 'green')
				# ax1.hist(listSizes, num_bins, facecolor='green', alpha=0.5)
				# ax1.set_xlim(0.0, 1.0)
				# ax1.set_ylim(0.0, mu)
				ax1.set_xlim(1, 5)
				ax1.set_xticks(range(1, len(listSizesRobot)))
				ax1.set_xticklabels(range(1, len(listSizesRobot)))
				ax1.set_xlabel('Size')
				ax1.set_ylabel('Number')
				ax1.set_title('Size of barcodes scanned')


				# Height of barcode
				width = 1
				bars = ax2.bar(range(len(listHeightRobot)), listHeightRobot, width = width, color = 'green')
				# ax2.hist(listHeight, num_bins, facecolor='green', alpha=0.5)
				# ax2.set_xlim(0.0, 1.0)
				# ax2.set_ylim(0.0, mu)
				ax2.set_xlim(1, 5)
				ax2.set_xticks(range(1, len(listHeightRobot)))
				ax2.set_xticklabels(range(1, len(listHeightRobot)))
				ax2.set_xlabel('Height')
				ax2.set_ylabel('Number')
				ax2.set_title('Height of barcodes scanned')

				fileName = os.path.splitext(os.path.basename(args.file))[0] + "Robot"
				plt.tight_layout()
				plt.savefig(os.path.join(CURRENT_FILE_PATH, fileName + ".png"), bbox_inches = 'tight')
				# plt.savefig(os.path.join(outputDir, "graphs" + str(numDir) + ".png"), bbox_inches = 'tight')
				# plt.show()
				plt.close()


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('file', help = "Log file")
	parser.add_argument('-t', '--two', help = "Two Robots", action = "store_true", default = False)
	args = parser.parse_args()

	main(args)
