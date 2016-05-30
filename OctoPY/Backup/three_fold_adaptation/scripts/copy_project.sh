#!/bin/bash
while read line
do
	echo "COPY PROJECT TO $line"
	ssh -n pi@"$line" rm -rf /home/pi/rpis/*
	echo "...removed old folder..."
	scp -r ../rpis pi@"$line":/home/pi/
	echo -e "\r"
done <./bots.txt
echo "done"
