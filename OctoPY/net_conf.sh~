#!/bin/bash

# Configure the server-router-robots network.


# Not necessary but might be needed when the connection has not previously been properly cut
sudo ifdown eth1

# This may display errors but they are not blocking
sudo ifup eth1

# This is used to confirm that the PC can communicate with the access point
ping 192.168.0.100

# It is also safer to validate that the adresse of the PC is correct: 192.168.0.210
ifconfig 

# Make sure the DHCP is properly stopped (not necessary but more cautious) and started
sudo /etc/init.d/isc-dhcp-server restart
