#!/usr/bin/env python3 

import io
import base64
import numpy as np
from PIL import Image
from threading import Lock
# import matplotlib.pyplot as plt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from FacerKnn import FacerKnn
# import time

TEST_IMAGE_PATH = 'resources/test_photo.jpg'

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
# facer = Facer('resources/encodings.npy', 'resources/faces_names.json')
facer = FacerKnn('resources/knn_model.clf', 'resources/encodings.npy', 'resources/faces_names.json')


@socketio.on('image_sink', namespace='/test')
def get_image(message):
    average = message['average']
    image_PIL = Image.open(io.BytesIO(base64.b64decode(message['data'].split(',')[1]))).convert('RGB')
    image_np = np.array(image_PIL)

    # image_PIL.show()
    # plt.imshow(image_np)
    # plt.show()
    # pil_img = Image.fromarray(image_np)
    # buff = io.BytesIO()
    # pil_img.save(buff, format="PNG")
    # image_string = base64.b64encode(buff.getvalue()).decode("utf-8")

    # start_time = time.time()
    who, path, coord = facer.find_nearest(image_np)
    print(who)
    # print("--- %s seconds ---" % (time.time() - start_time))

    with open(TEST_IMAGE_PATH, "rb") as image_file:
        image_string = base64.b64encode(image_file.read()).decode("utf-8")
    emit('my_response',
         {'data': image_string,
          'coord': coord})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
