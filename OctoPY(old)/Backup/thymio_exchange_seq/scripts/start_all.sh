#!/bin/sh
# python src/run_simulation.py localhost 55555 &
python src/run_simulation.py 192.168.1.101 55555 &
python src/run_simulation.py 192.168.1.102 55555 &
wait
