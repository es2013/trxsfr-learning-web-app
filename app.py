from flask import Flask
from flask import render_template, request
import requests
import json
import base64
import random
import os
import config
import mob_net_cls
import time

import util

app = Flask(__name__)

BASE_DIR = config.BASE_DIR

RAND_TRAIN_IMG_PATH =  os.path.join(BASE_DIR, 'images/ILSVRC/Data/DET/test')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_remote_image')
def get_remote_image():
    image_url = request.args.get('image_url')
    print(image_url)
    resp = requests.get(image_url)
    if resp.status_code == 200:
        return base64.b64encode(resp.content)

@app.route('/predict_mobilenet', methods = ['POST'])
def get_results():

    data = request.form
    #s = time.time()
    imageJSON = json.loads(data['json'])
    img_b64 = imageJSON['img']
    #print(img_b64)
    image_np = util.decode_b64_image_to_nparr_RGB(img_b64)
    print(image_np.shape)
    res_data =  mob_net_cls.predict(image_np)
    print(res_data)
    return json.dumps( {'data': res_data}, indent=4, separators=(',', ': '))

@app.route('/get_random_image_from_cache', methods = ['GET'])
def random_image():
    rand_file = random.choice(os.listdir( RAND_TRAIN_IMG_PATH))
    rand_file_path = os.path.join(RAND_TRAIN_IMG_PATH, rand_file)
    print(rand_file_path)
    with open(rand_file_path, 'rb') as f:
        print(f)
        return base64.b64encode(f.read())


@app.route('/api/<model_name>', methods = ['GET'])
def load_model(model_name):
    s = time.time()
    cls = mob_net_cls.CustomClassifier(project_name = model_name,
                                       model_name='sklearn-svc-acc-0.98824-2017-11-20-21-11-24.pkl',
                                       preprocess_funcs=[mob_net_cls.util_process_image, mob_net_cls.mobile_net_neck_predict])

    #image_json = json.loads(request.form['json'])
    #img_b64 = image_json['img']
    #image_np = util.decode_b64_image_to_nparr_RGB(img_b64)
    image_np = util.read_image_as_nparr_RGB('./images/elephant.jpeg', shape=(224, 224))
    #print(image_np.shape)
    res_data =  cls.predict_as_dict(image_np)
    print('Elapsed Time', time.time() - s)
    return json.dumps( {'data': res_data}, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    app.run(debug=True)