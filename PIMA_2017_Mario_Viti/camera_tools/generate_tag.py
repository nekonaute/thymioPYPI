import svgwrite
from svgwrite import cm
import numpy as np
import sys

"""
http://pythonhosted.org/svgwrite/overview.html
"""


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

def draw_bit_matrix(bit_mat, size):
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

def draw_tag(drawObj,lx,ly,area_ratio,num_bits,level_side,num_tag):
    drawObj.add(drawObj.rect(insert=(lx*cm,ly*cm), size=((level_side)*cm, (level_side)*cm), fill="black"))
    for i in range(4):
        fill = "black" if i%2 == 1 else "white"
        prev_level_side = level_side
        level_side = next_level(level_side,area_ratio)
        lx = next_left_top(prev_level_side,level_side) + lx
        ly = next_left_top(prev_level_side,level_side) + ly
        drawObj.add(drawObj.rect(insert=(lx*cm,ly*cm), size=(level_side*cm, level_side*cm), fill=fill))
    area_ratio = 1.25
    prev_level_side = level_side
    level_side = next_level(level_side,area_ratio)
    lx = next_left_top(prev_level_side,level_side) + lx
    ly = next_left_top(prev_level_side,level_side) + ly
    drawObj.add(drawObj.rect(insert=(lx*cm,ly*cm), size=(level_side*cm, level_side*cm), fill="black"))

    bit_mat = bit_matrix(num_tag,num_bits)
    draw_attrs = draw_bit_matrix(bit_mat,level_side)
    for draw_attr in draw_attrs:
        lt1, lt2 = draw_attr[0]
        lt1 += lx
        lt2 += ly
        size1, size2 = draw_attr[1]
        fill = draw_attr[2]
        drawObj.add(drawObj.rect(insert=(lt1*cm,lt2*cm), size=(size1*cm, size2*cm), fill=fill))

def main():
    # get params from argv
    if len(sys.argv) < 2:
        print "usage1: python generate_tag.py [number between 0-2^9 -1]\nusage2: python generate_tag.py all\nall will save 2*99 tags in .svg\n 6 x file tags to fit an A4 sheet."
    input_arg = (sys.argv[1])
    num_bits = 9
    area_ratio = 1.4
    level_side = 8.0
    lx = 0
    ly = 0
    distance = 0.5
    if input_arg == 'all':
        drawObj = svgwrite.Drawing('tag_'+`0`+'_'+`8`+'.svg', profile='tiny')#, width=`level_side`+'cm', height=`level_side`+'cm')
        for i in range(2**num_bits):
            num_tag = i
            if i!=0:
                draw_tag(drawObj,lx,ly,area_ratio,num_bits,level_side,num_tag)
                lx += level_side + distance
            if num_tag%2 == 0 and num_tag>0:
                lx = 0
                ly += level_side + distance
            if num_tag%6 == 0 and num_tag>0:
                drawObj.save()
                lx = 0
                ly = 0
                drawObj = svgwrite.Drawing('tag_'+`num_tag`+'_'+`num_tag+8`+'.svg', profile='tiny')#, width=`level_side`+'cm', height=`level_side`+'cm')
    else:
        num_tag = int(input_arg)
        drawObj = svgwrite.Drawing('tag_'+`num_tag`+'.svg', profile='tiny')#, width=`level_side`+'cm', height=`level_side`+'cm')
        draw_tag(drawObj,lx,ly,area_ratio,num_bits,level_side,num_tag)
        drawObj.save()

if __name__ == '__main__':
    main()
