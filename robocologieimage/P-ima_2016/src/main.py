 #!/usr/bin/python
 # -*- coding: utf-8 -*-
from master import Master
from utilities import load_refs, get_refs, get_classifier

# Do not modify
REFS = get_refs("../data/ref_markers_512bits.json")
NPZ_DATA, CLF_NAMEFILE = 'tags190316_isir_1', 'classifier190316_isir_1.pkl'
CAM = 'CAMERA'
VID = 'VIDEO'

# Edit here
## Project name
PROJECT_TITLE = "PIMA (2016) - Multiple Camera Robot Detection"

## Project files
LIVE = (1,)
FOO1 = [('../data/video/kinect/v1/2016-03-07-160118.webm',
       '../data/video/kinect/v1/2016-03-07-155725.webm',
       '../data/video/kinect/v1/2016-03-07-154756.webm'),
       ([21, 22, 23, 24, 25, 26, 27, 29, 20, 30, 31],
       [21, 22, 23, 24, 25, 26, 27, 29, 20, 30, 31],
       [21, 22, 23, 24, 25, 26, 27, 29, 20, 30, 31]),
       "KINECT_V1_ISIR"]

FOO2 = [('../data/video/kinect/v1/2016-03-17-010620.webm',
         '../data/video/kinect/v1/2016-03-17-011145.webm',
         '../data/video/kinect/v1/2016-03-17-012058.webm'),
        ([20, 30, 31],
        [20, 30, 31],
        [20, 30, 31]),
        "KINECT_V1_HOUSE"]

FOO3 = [('../data/video/kinect/v2/kinect04-24-23.mp4',
         '../data/video/kinect/v2/kinect04-29-27.mp4',
         '../data/video/kinect/v2/kinect04-31-41.mp4'),
        ([33, 28, 35],
        [33, 28, 35],
        [33, 28, 35]),
        "KINECT_V2_ISIR"]

# Edit mode
V0 = (CAM, LIVE, [], "LIVE", REFS)
V1 = (VID, FOO1[0], FOO1[1], FOO1[2], REFS)
V2 = (VID, FOO2[0], FOO2[1], FOO2[2], REFS)
V3 = (VID, FOO3[0], FOO3[1], FOO3[2], REFS)

# Choose a pill
CURRENT_MODE, CURRENT_ID, VALID_IDS, DESCR, CURRENT_REFS = V1

if __name__ == "__main__":
    # Active graphical interface (you need Tkinter)
    with_GUI = True

    # Initizalize world
    master = Master(PROJECT_TITLE, DESCR)

    # Setup controller and detectors according to mode and ids
    master.setup_controller(CURRENT_MODE, CURRENT_ID)
    master.setup_detectors(CURRENT_REFS, get_classifier(CLF_NAMEFILE), VALID_IDS)
    master.setup_interface(with_GUI)

    # Run the program
    master.run()

    # Collect data and store it
    master.collect_data(NPZ_DATA)

    # Evalute algorithm
    master.evaluation()

    # When everything done, kill tkinter interface and release all capture
    master.kill()
