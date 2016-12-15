 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from master import Master
from utilities import get_refs

# Do not modify
DEFAULT_REFS = "../data/ref_markers_512bits.json"
PROJECT_TITLE = "PIMA (2016) - Multiple Camera Robot Detection"
WITH_GUI = True

if __name__ == "__main__":
    # Initizalize world
    master = Master(PROJECT_TITLE, WITH_GUI)

    # Setup controller and detectors according to mode and ids

    master.setup_parameters()
    if WITH_GUI:
        master.setup_interface()
        master.setup_preferences_gui()
    master.setup_controller()
    master.setup_detectors(DEFAULT_REFS)
    if WITH_GUI:
        master.setup_detection_gui()

    # Open all cameras and videos
    master.open_captures()

    # Run the program
    master.run()

    # Collect data and store it
    # master.collect_data(NPZ_DATA)

    # When everything done, kill tkinter interface and release all capture
    master.kill()
