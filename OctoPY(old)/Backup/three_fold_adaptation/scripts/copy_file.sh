#!/bin/bash
while read line
do
	echo "COPY '$1' TO $line"
	scp ../rpis/"$1" pi@"$line":/home/pi/rpis/$1 &
	echo -e "\r"
done <./bots.txt
wait