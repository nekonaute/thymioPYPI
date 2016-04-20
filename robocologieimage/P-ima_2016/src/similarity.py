 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import numpy as np
import random

def distanceBetweenMatrix(tag1, tag2):
    consecutive_color = 1
    list_consecutive = []
    for x in range(1,len(tag1)-1):
        for y in range(1,len(tag1)-1):
            if tag1[x, y] == tag2[x, y]:
                consecutive_color += 1
            else:
                list_consecutive.append(consecutive_color)
                consecutive_color = 1
    for y in range(1,len(tag1)-1):
        for x in range(1,len(tag1)-1):
            if tag1[x, y] == tag2[x, y]:
                consecutive_color += 1
            else:
                list_consecutive.append(consecutive_color)
                consecutive_color = 1
    if list_consecutive:
        list_consecutive[-1] += consecutive_color
    else:
        list_consecutive.append(consecutive_color)
    return sum((1+np.array(list_consecutive))**2) - len(list_consecutive)

def similarity(tags):
    """ Return id of the least similarity tag with others """
    dist = np.zeros((len(tags),))
    for i in range(0, len(tags)):
        for j in range(0, len(tags)):
            dist[i] += distanceBetweenMatrix(tags[i][0], tags[j][0])
    return np.linalg.norm(dist)

def similarity_combinaison(tags, combi_length):
    assert combi_length < len(tags)

    best_combi = [random.sample(tags, 1)]
    print "random first pick (without constraint), added tag: {}".format(get_identifiant([best_combi[-1]], tags))
    vu = []
    i = 0
    curr_threshold = 200
    while not len(best_combi) == combi_length:
        remaining_tags = [tag for tag in tags if not (tag.tolist() in best_combi or tag.tolist() in vu)]
        random_tag = random.sample(remaining_tags, 1)
        if similarity(best_combi + [random_tag]) < curr_threshold:
            print "similarity score: {:f} (threshold: {}), added tag: {}".format(similarity(best_combi + [random_tag]), curr_threshold, get_identifiant([random_tag], tags))
            best_combi.append(random_tag)
            i = 0
            vu = []
        elif i > len(remaining_tags)**2:
            curr_threshold += 1
        else:
            vu.append(random_tag)
        i += 1
    print "Random-based similarity search ({} elements, {} score) : {}".format(combi_length, similarity(best_combi), get_identifiant(best_combi, tags))
    return best_combi, get_identifiant(best_combi, tags)

def get_identifiant(tags, references):
    return [references.tolist().index(np.array(tag).tolist()[0]) for tag in tags]

if __name__ == "__main__":
    # Goal is to find a combinaison of tags with as less inter-similarity
    # as possible.

    # Loading tags
    from main import REFS
    from utilities import load_refs
    tags = load_refs("../data/ref_markers_512bits.json")


    # Size of the tag combinaison
    combi_length = 3

    arrays, indexes = similarity_combinaison(tags, combi_length)
