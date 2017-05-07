# -*- coding: utf-8 -*-
import cv2
import os
import tools

def print_template_resolution():
    """
    Show the templates for each distance (15,18,20,30,50,65) in cm
    Taken with the current resolution: if so
    """
    path = tools.get_template_path()
    list_img = []
    try:
        list_img = sorted(os.listdir(path))
    except:
        print "No templates found for this resolution"
        return None
    for i,img_name in enumerate(list_img):
        cv2.destroyAllWindows()
        img = cv2.imread(path+img_name)
        cv2.imshow(str(img_name),img)
        cv2.waitKey(0)
        

def real_percentages_pie(classification):
    true_pos = true_neg = 0
    for val in classification.values()
        if val==[]:
            true_neg +=1
        else:
            true_pos += 1
    labels = 'True positives', 'True negatives'
    sizes = [true_pos,true_neg]
    #colors = ['yellowgreen', 'lightskyblue']
    explode = (0, 0.1)  # only "explode" the 2nd slice

    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.savefig(tools.PLOT_PATH+"expected_percentages.png")
    print "Pie chart of classification saved"
    plt.show()
    
