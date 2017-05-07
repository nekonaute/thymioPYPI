

TRIANGLE_TYPE = 'triangle'
SQUARE_TYPE = 'square'
DOUBLE_SQUARE_TYPE = 'double_square'

AREA_RATIO_KEY = 'area_ratio'
DIAGONAL_KEY = 'diagonal'

tags_settings = {
                    'double_square' : {
                        'area_ratio' : 1.44,
                        'diagonal' : 7.5,#cm
                        'bits' : 9
                    },
                }

camera_settings = {
    'resolution' : (640,480),
    'framerate' : 30,
    'frame': {
        'format' : "bgr",
        'use_video_port' : True
    },
    'awb' : False,
    'awb_gains' : (0.9,0.9), # allowed 0-1.9
    'aexposure' : True,
}
