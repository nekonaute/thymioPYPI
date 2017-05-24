import numpy as np

# valid_1
# full light environment
# automatic canny

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
