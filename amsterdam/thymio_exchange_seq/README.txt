Code for letting two (or more) Thymios equipped with a RaspberryPi, a battery and a WiFi dongle broadcast TCP messages over a WiFi router. 
Each message represents a sequence of movements [left, right, forward, backward]. When a robot receives a message, it queues it in an incoming list. 
Each robot goes through the following phases:
1. Move: if the incoming list is empty, the robot generates a random sequence of movements and executes it. 
Otherwise, it chooses a random message from the incoming list and executes it.
2. Sleep: the robot rests for 2 seconds and does nothing (could be seen as a "processing" phase).
3. Generate: the robot generates a random sequence of movements and broadcast it to all the other robots in the network.
After 10 runs (system parameter) all the Thymios stop.

Code is tested on Raspbian 2015-01-31 with Python 2.7 and aseba 1.3.3.
Every RPi is configured to boot up and connect to the network with a fixed IP. After booting up, it automatically runs the script "scripts/_init_thymio.sh" (must be configured with the full path of the "exchange_seq.py" file). This is needed because if these commands are run from an SSH shell, then asebamedulla will assign the dbus only to the first one to run the command and the other Thymios will not work.
The file "config.json" has to be configured for each robot. 
To run the simulation on all robots, run the script "scripts/start_all.sh". To start it on just one robot, run "python src/run_simulation.py" followed by the IP address and the port of the RPi (port must be 55555 at the moment).
To stop the simulation on all robots, run the script "scripts/stop_all.sh". To stop it on just one robot, run "python src/run_simulation.py ipAddress port --stop".
During the simulation a log file is generated and placed under the /log folder.

