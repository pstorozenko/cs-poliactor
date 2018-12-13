#!/usr/bin/env python3 

import io
import base64
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib
# from matplotlib.backends.backend_tkagg import FigureCanvasAgg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import seaborn as sns
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from FacerKnn import FacerKnn

TEST_IMAGE_PATH = 'resources/test_photo.jpg'

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
facer = FacerKnn('resources/knn_model.clf', 'resources/actors_photos_encodings.pkl')

matplotlib.use('agg')
sns.set(rc={'figure.figsize': (20, 20)})
fig = plt.figure()
faces = facer.get_base_pca()
ax = sns.scatterplot(data=faces, x='pca_0', y='pca_1', s=1, color='black')
for i, text in enumerate(faces.init.values):
    plt.text(faces.pca_0[i], faces.pca_1[i], text, fontsize=11)
ax.xaxis.label.set_visible(False)
ax.yaxis.label.set_visible(False)
# box = ax.get_position()
# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.show(block=False)


@socketio.on('image_sink', namespace='/test')
def get_image(message):
    average = message['average']
    frames = int(message['frames'])
    image_PIL = Image.open(io.BytesIO(base64.b64decode(message['data'].split(',')[1]))).convert('RGB')
    image_np = np.array(image_PIL)

    # start_time = time.time()
    who, path, coord, pca = facer.find_nearest(image_np, frames)
    print(who, path)
    # print("--- %s seconds ---" % (time.time() - start_time))
    if path:
        with open(path, "rb") as image_file:
            image_string = base64.b64encode(image_file.read()).decode("utf-8")
        plt.scatter(pca[0], pca[1], s=200, marker='x', color='red')
        plt.draw()
        canvas = FigureCanvasAgg(fig)
        png_output = io.BytesIO()
        canvas.print_png(png_output)
        plot_string = base64.b64encode(png_output.getvalue()).decode("utf-8")
    else:
        blank_img = Image.fromarray(np.ones_like(image_np, dtype='uint8') * 255)
        buff = io.BytesIO()
        blank_img.save(buff, format="PNG")
        image_string = base64.b64encode(buff.getvalue()).decode("utf-8")
        plot_string = base64.b64encode(buff.getvalue()).decode("utf-8")
        who = [" "]

    emit('my_response',
         {
             'actor': who[0],
             'image': image_string,
             'plot': plot_string,
             'coord': coord
         })


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
