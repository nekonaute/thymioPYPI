echo 'copy to pi@192.168.1.101'
ssh pi@192.168.1.101 rm -rf /home/pi/thymio_exchange_seq/
scp -r /media/Data/GoogleDrive/devices/master_project/thymio_exchange_seq pi@192.168.1.101:/home/pi/
echo 'copy to pi@192.168.1.102'
ssh pi@192.168.1.102 rm -rf /home/pi/thymio_exchange_seq/
scp -r /media/Data/GoogleDrive/devices/master_project/thymio_exchange_seq pi@192.168.1.102:/home/pi/
