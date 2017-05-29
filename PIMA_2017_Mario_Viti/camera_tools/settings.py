
TRIANGLE_TYPE = 'triangle'
SQUARE_TYPE = 'square'
DOUBLE_SQUARE_TYPE = 'double_square'

AREA_RATIO_KEY = 'area_ratio'
SIDE_KEY = 'side'

"""
double_square tag (section)

    level -------------------------------
    | next level-----------------------  |
    | | next level-------------------  | |
    | | | next next level----------  | | |
    | | | | next next level----  | | | | |


"""

tags_settings = {
                    'double_square' : {
                        'area_ratio' : 1.4,
                        'side' : 4.0, #cm of the innermost next netx level
                        'bits' : 9
                    },
                }

# referr to http://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
camera_settings = {
    'resolution' : (640, 480),
    'framerate' : 30,
    'frame_resize_resolution' : (640, 480),
    'frame': {
        'format' : "bgr",
        'use_video_port' : True
    },
    'awb' : False,
    'awb_gains' : (1.0,1.0), # allowed 0-1.9
    # motion: motion setting minimize motion blur buy augmenting shutter speed;
    # off: sets exposure time to shutter speed depending on the framerate;
    # on: autoexposure;
    'exposure_mode' : 'motion' , #'off', #'on'
}
