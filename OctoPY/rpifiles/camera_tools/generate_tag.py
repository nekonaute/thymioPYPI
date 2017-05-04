import numpy as np

def generate_tag(tag_matrix,size_scale):
    """
        tag_matrix is a matrix of 0 and 1s
        the tag_matrix.shape is the shape of the tag
        return image is in UINT8
    """
    s = size_scale
    y,x = tag_matrix.shape
    image = np.zeros((y*size_scale,x*size_scale),dtype=np.uint8)
    for i in range(y):
        for j in range(x):
            image[i*s:(i+1)*s,j*s:(j+1)*s] = tag_matrix[i,j]*255
    return image

def calc_id(tag_matrix):
    acc = 0
    y,x = tag_matrix.shape
    for i in range(y):
        for j in range(x):
            acc += 2**(i*y+j)*tag_matrix[i,j]


tag_matrix = np.array([[0,0,1],[1,0,0],[0,1,0]])
print generate_tag(tag_matrix,2)
