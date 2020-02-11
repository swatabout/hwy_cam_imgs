?
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 11:27:56 2019

@author: Sierra Watkings
"""

from PIL import Image
import os.path
import io
import numpy as np
import matplotlib.pyplot as plt
import pymongo 
import scipy
import json

def threshold(histogram, bins, height, distance):
    peaks, _ = scipy.signal.find_peaks(hist, height = height, distance=distance)
    points = bins[peaks]
    thresh = points[0] + (np.diff(points) / 2)
    return thresh

def calculate_brightness(image):
    histogram = image.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale
    
bright = []
if __name__ == '__main__':
    path = "C:/Users/Sierra Watkings/Documents/Repos/proj-SWATKINS-HWY_Camera_Classification/notebooks/"
    
    for f in os.listdir(path):
        for i in range(45): # true 24hr window 45 images for this 
            if f.endswith("%d.png" % i):
                #img=io.BytesIO(list[i].read())
                pic = Image.open(f)
                image = Image.open(f).convert('LA')
                bright.append(calculate_brightness(image))
                
    # histogram the brightness 
    hist, bin_edges = np.histogram(bright, np.histogram_bin_edges(bright, bins='stone'))
    bincenters = np.array([0.5 * (bin_edges[i] + bin_edges[i+1]) for i in range(len(bin_edges)-1)])
    th = threshold(hist, bincenters, 7, 10)
    print(th)    
    #for image in list():
        ## add night and day as attribute
        #if bright >= th: 
        #    data["image"].append({'Timeofday':'Day'})
        #if bright < th:
        #    data["image"].append({'Timeofday':'Night'})
        
        ##push back to mongodb





























