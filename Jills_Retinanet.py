from imageai.Detection import ObjectDetection
import os, numpy as np
import pandas as pd
from IPython.display import Image

def detect_object(image):

    try:
        # set path to find model
        execution_path = os.getcwd()
        detector = ObjectDetection()
        detector.setModelPath(os.path.join(execution_path, 'resnet50_coco_best_v2.0.1.h5'))
        detector.setModelTypeAsRetinaNet()
        detector.loadModel(detection_speed = "fast")

    except:
        logging.error('Transfer model failed to load')

        # bounding boxes in images
    try:
        boxes = []
        custom_objects = detector.CustomObjects(car=True, truck=True)
        detections = detector.detectCustomObjectsFromImage(input_image = image,
                                                      output_image_path = os.getcwd(), # hopefully same path as the container
                                                      custom_objects = custom_objects, minimum_percentage_probability=20) ##might want to change that prob percentage
    except:
        logging.error("Couldn't put in bounding boxes on custom objects")

    try:
        for eachObject in detections:
            boxes.append(eachObject["name"], image)

            Image(image) #show image in api
    except:
        logging.error("No boxes to be found in detection")

    try:
         # convert list of objects to dataframe
        df = pd.DataFrame.from_records(boxes, columns = ['Object', 'Image_Name', 'Probability', 'box_ppoints']) # with probablities
        df['Image_Name'] = "C:/Users/swatkins/Downloads/GA000000016040_2020-01-23_15h_40m.png"
         
        #split image_name column to get date, time and name into separated columns 
        strdf = df['Image_Name'].str.replace('/', '_')
        strdf = strdf.str.replace('.', '_')
        strdf = strdf.str.split('_', expand = True) #ouput type is dataframe 
        
        df['Camera_ID'] = strdf[strdf.columns[4]]
        df['Date'] = strdf[strdf.columns[5]]
        df['Hour'] = strdf[strdf.columns[6]]
        df['Minute'] = strdf[strdf.columns[7]]
    #    df_count = df['Object', 'Image_name'] # without probablities
    
    except:
        logging.error('Could not convert boxes to dataframe')

    try:
        #sum the counts
        counts = df_count.groupby(['Object'])[['Count']].sum()
    except:
        logging.error('Could not count objects in boxes')

    return counts

