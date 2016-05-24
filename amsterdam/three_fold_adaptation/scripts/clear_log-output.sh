#!/bin/sh
while read line
do
	echo "CLEARING OUTPUT & LOG $line"
	if [ -n "$1" ]
	then
		ssh -n pi@"$line" rm -rf /home/pi/rpis/output/"$1" &
	else
		ssh -n pi@"$line" rm -rf /home/pi/rpis/log_main/* /home/pi/rpis/output/* &
	fi
done <./bots.txt
wait
