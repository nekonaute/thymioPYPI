#!/bin/bash
mkdir ../received_outputs/"$1"/
while read line
do
	echo "COPY '$1' files FROM $line"
	scp pi@"$line":/home/pi/rpis/output/"$1"/"$1"_out.txt ../received_outputs/"$1"/"$1"_"$line"_out.txt
	scp pi@"$line":/home/pi/rpis/output/"$1"/"$1"_sim_debug.log ../received_outputs/"$1"/"$1"_"$line"_sim_debug.log
	echo -e "\r"
done <./bots.txt
cp ../rpis/algorithm.py ../received_outputs/"$1"/
cp ../rpis/parameters.py ../received_outputs/"$1"/
wait