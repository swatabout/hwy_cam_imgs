#!/usr/bin/env python3
import io, boto3, logging, sqlalchemy as sql, os, numpy as np
from PIL import Image
import matplotlib.image as mpim

def list_files(/path/to/images/, Image_Name):

    filelist = []
    for image in /path/to/images/:
        filelist.append(image)
        
    if len(filelist) > 0 is False:
        logging.error("Image list is empty")

    return filelist



