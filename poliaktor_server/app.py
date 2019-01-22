#!/usr/bin/env python3 

import io
import base64
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from FacerKnn import FacerKnn

TEST_IMAGE_PATH = 'resources/test_photo.jpg'

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
facer = FacerKnn('resources/knn_model.clf', 'resources/actors_photos_encodings.pkl')


@socketio.on('reset_plot', namespace='/test')
def reset_plot(_):
    facer.reset_plot()


@socketio.on('disconnect')
def on_disconnect():
    global disconnected
    disconnected = '/'
    facer.reset_plot()


@socketio.on('image_sink', namespace='/test')
def get_image(message):
    # start_time = time.time()
    frames = int(message['frames'])
    image_PIL = Image.open(io.BytesIO(base64.b64decode(message['data'].split(',')[1]))).convert('RGB')
    image_np = np.array(image_PIL)

    who, path, coord, pca = facer.find_nearest(image_np, frames)
    print(who, path)
    if path:
        with open(path, "rb") as image_file:
            image_string = base64.b64encode(image_file.read()).decode("utf-8")
    else:
        blank_img = Image.fromarray(np.ones_like(image_np, dtype='uint8') * 255)
        buff = io.BytesIO()
        blank_img.save(buff, format="PNG")
        image_string = base64.b64encode(buff.getvalue()).decode("utf-8")

        who = ["No one :("]

    fig = facer.get_plot(pca[0], pca[1])
    canvas = FigureCanvasAgg(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    plot_string = base64.b64encode(png_output.getvalue()).decode("utf-8")

    emit('my_response',
         {
             'actor': who,
             'image': image_string,
             'plot': plot_string,
             'coord': coord
         })

    # print("--- %s seconds ---" % (time.time() - start_time))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
