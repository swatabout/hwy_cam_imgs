#!/usr/bin/env python3
import io, boto3, logging, sqlalchemy as sql, os, numpy as np, glob
from PIL import Image
import matplotlib.image as mpim

def list_files(Image_Name):

    os.chdir(/path/to/images)
    
    filelist = []
    for image in glob.glob(/path/to/images/Image_Name):
        filelist.append(image)
        
    if len(filelist) > 0 is False:
        logging.error("Image list is empty")

    return filelist



