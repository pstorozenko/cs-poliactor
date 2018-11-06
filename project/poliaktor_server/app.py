import io
import base64
import numpy as np
from PIL import Image
from threading import Lock
import matplotlib.pyplot as plt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@socketio.on('image_sink', namespace='/test')
def get_image(message):
    image_PIL = Image.open(io.BytesIO(base64.b64decode(message['data'].split(',')[1])))
    # image_PIL.show()
    image_np = np.array(image_PIL)
    # plt.imshow(image_np)
    # plt.show()
    pil_img = Image.fromarray(image_np)
    buff = io.BytesIO()
    pil_img.save(buff, format="PNG")
    new_image_string = base64.b64encode(buff.getvalue()).decode("utf-8")
    emit('my_response',
         {'data': new_image_string})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


if __name__ == '__main__':
    socketio.run(app, debug=True)
