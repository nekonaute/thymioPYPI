import svgwrite
from svgwrite import cm

import numpy as np
"""
http://pythonhosted.org/svgwrite/overview.html
"""

import sys
num_tag = int(sys.argv[1])

def bit_matrix(num,bits):
    assert num < 2**bits
    sqbits = int(np.sqrt(bits))
    bit_mat = np.zeros((sqbits,sqbits))
    bin_str = [ '0' for i in range(bits)]
    len_b_string = len(bin(num)[2:])
    bin_str[-len_b_string:] = bin(num)[2:]
    for i in range(sqbits):
        for j in range(sqbits):
            bit_mat[i,j] = bin_str[i*sqbits+j]
    return np.fliplr(np.fliplr(bit_mat.T).T).T

def draw_bit_matrix(bit_matrix, size):
    """
    [[insert,size,fill],
     ...]
    """
    draw_attrs = []
    sqbits = bit_mat.shape[0]
    dx = size/float(sqbits)
    for i in range(sqbits):
        for j in range(sqbits):
            insert = tuple([dx*i,dx*j])
            size = tuple([dx,dx])
            fill = "white" if bit_mat[j,i] == 1 else "black"
            draw_attrs += [ [insert, size, fill] ]
    return draw_attrs

def next_level(level_side,area_ratio):
    return np.sqrt((level_side**2)/area_ratio)

def next_left_top(level_side,next_level_side):
    lt = level_side/2.-(next_level_side/2.)
    return lt

# get params from argv

num_bits = 9
area_ratio = 1.4
level_side = 7.5
lt = 0
drawObj = svgwrite.Drawing('tag_'+`num_tag`+'.svg', profile='tiny')#, width=`level_side`+'cm', height=`level_side`+'cm')
drawObj.add(drawObj.rect(insert=(lt*cm,lt*cm), size=(level_side*cm, level_side*cm), fill="black"))
for i in range(4):
    fill = "black" if i%2 == 1 else "white"
    prev_level_side = level_side
    level_side = next_level(level_side,area_ratio)
    lt = next_left_top(prev_level_side,level_side) + lt
    drawObj.add(drawObj.rect(insert=(lt*cm,lt*cm), size=(level_side*cm, level_side*cm), fill=fill))
area_ratio = 1.25
prev_level_side = level_side
level_side = next_level(level_side,area_ratio)
lt = next_left_top(prev_level_side,level_side) + lt
drawObj.add(drawObj.rect(insert=(lt*cm,lt*cm), size=(level_side*cm, level_side*cm), fill="black"))

bit_mat = bit_matrix(num_tag,num_bits)
draw_attrs = draw_bit_matrix(bit_mat,level_side)
for draw_attr in draw_attrs:
    lt1, lt2 = draw_attr[0]
    lt1 += lt
    lt2 += lt
    size1, size2 = draw_attr[1]
    fill = draw_attr[2]
    drawObj.add(drawObj.rect(insert=(lt1*cm,lt2*cm), size=(size1*cm, size2*cm), fill=fill))

print bit_mat
drawObj.save()
