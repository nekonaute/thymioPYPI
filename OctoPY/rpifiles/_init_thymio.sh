#!/bin/sh

hostIP=$1

sleep 5
(asebamedulla "ser:device=/dev/ttyACM0" &)
sleep 1

if [ -z $hostIP ]
then
	python /home/pi/dev/thymioPYPI/medusa/rpifiles//exchange_seq.py -d &
else
	python /home/pi/dev/thymioPYPI/medusa/rpifiles/exchange_seq.py -d -i $hostIP &
fi
