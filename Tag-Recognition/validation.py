import numpy as np
import Queue
import cv2

track_eval_name = 'evaulationg_1'
track_eval = {'a_vals': [], 'inter_ds': [], 'dists': [], 'GTcs_x': [], 'GTcs_y': [] , 'STcs_x': [], 'STcs_y': []}
motion_eval_name = 'eval_motion'
motion_eval = {"tracking":[]}

def eval_cont():
	arr = np.array(motion_eval['tracking'])
	return np.sum(arr)/float((arr.shape[0]))

def update_motion_eval(found):
	motion_eval['tracking'] += [found]
	
def save_motion_eval():
    out_file = open("./validations/" + motion_eval_name + ".json","w")
    out_file.write(`motion_eval`)
    out_file.close()

def update_track_eval(a_val, inter_d, dist, GTc, STc):
    track_eval['a_vals'] += [a_val]
    track_eval['inter_ds'] += [inter_d]
    track_eval['dists'] += [dist]
    track_eval['GTcs_x'] += [GTc[0]]
    track_eval['GTcs_y'] += [GTc[1]]
    track_eval['STcs_x'] += [STc[0]]
    track_eval['STcs_y'] += [STc[1]]

def save_track_eval():
    out_file = open("./track_eval/" + track_eval_name + ".json","w")
    out_file.write(`track_eval`)
    out_file.close()

def inte_dist(GT,ST):
    return np.linalg.norm(np.array(GT[0])-np.array(ST[0]))

def A_intersect(GT,ST,frame):
    imGT = np.zeros(frame.shape)
    imST = np.zeros(frame.shape)
    cv2.fillConvexPoly(imGT,GT,0.5)
    cv2.fillConvexPoly(imST,ST,0.5)
    A_ST = np.sum(imST)*2
    A_GT = np.sum(imGT)*2
    A_int = np.sum(np.floor(imGT+imST))
    A_uni = A_ST + A_GT - A_int
    A_val = A_int/float(A_uni)
    return A_val

def to_rgb_image(frame):
    rgb_image = np.zeros((frame.shape[0],frame.shape[1],3),dtype=np.uint8)
    rgb_image[:,:,0] = frame
    rgb_image[:,:,1] = rgb_image[:,:,0]
    rgb_image[:,:,2] = rgb_image[:,:,0]
    return rgb_image


validation_name = 'valid_7_full_light_automatic_canny_rot'
validation = {

    'tags': {
        '65': {'pos':(0.1,50.0), 'orient':45., 'dist': 0.,'estimate_d':[], 'mean_d':0., 'std_d': 0., 'mse_d': 0., 'hits':0., 'hit_rel_freq': 0.},
        '3':{'pos':(30.001,75.0), 'orient':45., 'dist': 0.,'estimate_d':[], 'mean_d':0., 'std_d': 0., 'mse_d': 0., 'hits':0., 'hit_rel_freq': 0.},
    },
    'fp' : {'count':0.}
}

def cartesian_to_polar((x,y)):
    if np.abs(x) <0.0001:
        x = 0.0001
    if np.abs(y) <0.0001:
        y = 0.0001
    r = np.sqrt(x**2 + y**2)
    angle = np.arctan(y/float(x))
    return r,angle

def update(ids,dists):
    for i in range(len(ids)):
        try:
            validation['tags'][''+`ids[i]`]['estimate_d'] += [dists[i]]
            validation['tags'][''+`ids[i]`]['hits'] += 1.
        except KeyError, e:
            validation['fp']['count'] += 1.

def compute_stats():
    max_val = 0.
    for k in validation['tags'].keys():
        max_val = validation['tags'][k]['hits'] if validation['tags'][k]['hits'] > max_val else max_val
    for k in validation['tags'].keys():
        mean = np.mean(np.array(validation['tags'][k]['estimate_d']))
        std = np.std(np.array(validation['tags'][k]['estimate_d']))
        real_d, angle = cartesian_to_polar(validation['tags'][k]['pos'])
        validation['tags'][k]['dist'] = real_d
        mse = np.mean((np.array(validation['tags'][k]['estimate_d']) - real_d)**2)
        validation['tags'][k]['mean_d'] = mean
        validation['tags'][k]['std_d'] = std
        validation['tags'][k]['mse_d'] = mse
        validation['tags'][k]['hit_rel_freq'] = validation['tags'][k]['hits']/float(max_val) if max_val>0. else 0.

def save_stats():
    out_file = open("./validations/" + validation_name + ".json","w")
    out_file.write(`validation`)
    out_file.close()
