#!/bin/sh
sleep 5
(asebamedulla "ser:device=/dev/ttyACM0" &)
sleep 1
python /media/Data/GoogleDrive/devices/master_project/thymio_exchange_seq/src/exchange_seq.py -d
