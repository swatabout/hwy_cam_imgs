from flask import Flask, request, jsonify
#from flask_sqlalchemy import SQLAlchemy
from Jills_RetinaNet import setup_detector, pull_con, detect_objects, pushtosql
import logging

app = Flask(__name__)

logging.info('App begins')
@app.route('/counts')

def predict():

    Image_Name = request.args.get('Image_Name')
    logging.info('Pulling imgs from aws')

    crop_img_list, fnamelist = pull_con(Image_Name)
    #logging.error('Could not pull images from s3 bucket')

    logging.info('Setting up Detection Model')
    detector = setup_detector(crop_img_list, fnamelist)
    logging.error('Cannot setup detector')

    logging.info('Obtaining predicted counts from images')
    counts, boxes = detect_objects(detector, crop_img_list, fnamelist)
    logging.error('Issue with counting objects in images')

    #return '''%s, length of crop_img_list : %s, length of fnamelist : %s /n
    #            counts = %s ''' % (Image_Name, len(crop_img_list), len(fnamelist), counts)

    con_counts = pushtosql(counts)

    return '''%s /n
                %s ''' % (counts, con_counts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
