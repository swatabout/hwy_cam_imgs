from flask import Flask, request, jsonify
from list_files import list_files
from model import setup_detector, detect_objects
import logging

app = Flask(__name__)

logging.info('App begins')
@app.route('/counts')

def predict():

    Image_Name = request.args.get('Image_Name')
    logging.info('Get image name from API call')

    filelist = list_files(Image_Name)
    logging.info('Get filelist'l)
    
    logging.info('Getting predicted counts from images')
    counts, boxes = detect_objects(detector, filelist)
    logging.error('Issue with counting objects in images')

    return '''%s /n
                %s ''' % (counts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
