

TRIANGLE_TYPE = 'triangle'
SQUARE_TYPE = 'square'
DOUBLE_SQUARE_TYPE = 'double_square'

AREA_RATIO_KEY = 'area_ratio'
SIDE_KEY = 'side'

tags_settings = {
                    'double_square' : {
                        'area_ratio' : 1.4,
                        'side' : 3.9,#cm
                        'bits' : 9
                    },
                }

camera_settings = {
    'resolution' : (640, 480),
    # referr to http://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
    'framerate' : 30,
    'frame_resize_resolution' : (640, 480),
    'frame': {
        'format' : "bgr",
        'use_video_port' : True
    },
    'awb' : False,
    'awb_gains' : (1.1,1.1), # allowed 0-1.9
    'aexposure' : False, #sets exposure time to shutter speed
}
