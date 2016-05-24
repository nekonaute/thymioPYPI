import time
import json
import pickle

from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename

PREV_PARAM_FILENAME = "temp_parameters.json"

def get_default_parameters():
    return {
        "captures": [],
        "eps": 0.1,
        "existing_tags": "[]",
        "kernel": 3.0,
        "max_contour_area": 800.0,
        "max_dist": 0.095,
        "method": 0.0,
        "min_contour_area": 50.0,
        "min_dist": 0.005,
        "record": 0,
        "sigma": 0.1,
        "record_name": "record_"+time.strftime("%Y%m%d-%H%M%S"),
        "time": time.strftime("%Y%m%d-%H%M%S")
    }

def open_json(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data

def load_parameters(filename):
    try:
        parameters = open_json(filename)
    except IOError:
        print("Parameters '{}' not found!".format(filename))
    else:
        return parameters

def save_parameters(parameters, filename=PREV_PARAM_FILENAME):
    if filename==PREV_PARAM_FILENAME:
        print("TempSave")
    with open(filename, 'w') as fp:
        json.dump(parameters, fp, sort_keys=True, indent=4)

def save_acquisition(data, record_name, parent_):
    filename = asksaveasfilename(parent=parent_, initialfile=record_name+".pkl")
    with open(filename, 'wb') as fp:
        pickle.dump(data, fp)
