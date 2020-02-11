#!/usr/bin/env python3
import io, boto3, logging, sqlalchemy as sql, os, numpy as np
from PIL import Image
import matplotlib.image as mpim
import os, config as cfg

def get_images(Username, Access_Key_ID, Secret_Access_Key):

    try:
        session = boto3.Session(Access_Key_ID, Secret_Access_Key)

    except:
        logging.error("session wasn't established", exec_info = True)
    try:
        s3 = session.resource('s3')
    except:
        logging.error("session didn't connect to s3")
    try:
        bucket = s3.Bucket('statictrafficcameras')
    except:
        logging.error("session didn't connect to s3 bucket")

    return bucket

def list_files(bucket, Image_Name):

    filelist = []
    fnamelist = []
    for file in bucket.objects.filter(Prefix = Image_Name):
        filelist.append(file)
        fnamelist.append(file.key)

    if len(filelist) > 0 is False:
        logging.error("Image list is empty")

    return filelist, fnamelist

def arrange_imgs(filelist):

    crop_img_list = []
    for i in range(len(filelist)):
        decode = io.BytesIO(filelist[i].get()['Body'].read())
        img = Image.open(decode)
        crop_img = img.crop(cfg.aws['crop_area'])
        crop_img.save('testimg_%s.png' %i, 'PNG')
        crop_img_list.append('testimg_%s.png' %i)

    if len(crop_img_list) > 0 is False:
        logging.error(':crop_img_list is empty')


    return crop_img_list

def sql_conn(Server, Database, PWD, UID):

    try:
        engine = sql.create_engine(f'mssql+pymssql://{UID}:{PWD}@{Server}/{Database}')
    except:
        logging.error('Sql engine did not generate')

    try:
        con = engine.connect()
    except:
        logging.error('Sql connection failed')

    return con

