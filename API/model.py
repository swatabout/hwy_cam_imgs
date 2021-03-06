from imageai.Detection import ObjectDetection
import os, numpy as np, pandas as pd

def detect_object(filelist):

    try:
        # set path to find model
        execution_path = os.getcwd()
        detector = ObjectDetection()
        detector.setModelPath(os.path.join(execution_path, 'resnet50_coco_best_v2.0.1.h5'))
        detector.setModelTypeAsRetinaNet()
        detector.loadModel(detection_speed = "fast")

    except:
        logging.error('Transfer model failed to load')
    
    boxes = []
    for image in len(filelist):
        # bounding boxes in images
    try:
        boxes = []
        custom_objects = detector.CustomObjects(car=True, truck=True)
        detections = detector.detectCustomObjectsFromImage(input_image = image,
                                                      output_image_path = '%s_new.png' % filelist[image],
                                                      custom_objects = custom_objects, minimum_percentage_probability=20) 
        logging.error("Couldn't put in bounding boxes on custom objects")

    try:
        for eachObject in detections:
            boxes.append((eachObject["name"], filelist[image]))
    except:
        logging.error("No boxes to be found in detection")

    try:
         # convert list of objects to dataframe
        df = pd.DataFrame.from_records(boxes, columns = ['Object', 'Image_Name', 'Probability', 'box_points']) # with probablities
        df_count = df['Object', 'Image_name'] # without probablities
    
    except:
        logging.error('Could not convert boxes to dataframe')

    try:
        #sum the counts
        counts = df_count.groupby(['Object'])[['Count']].sum()
    except:
        logging.error('Could not count objects in boxes')

    return counts

