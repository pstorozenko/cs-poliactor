from PIL import Image
import io, base64
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import matplotlib.pyplot as plt
import numpy as np

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@socketio.on('image_sink', namespace='/test')
def get_image(message):
    image_PIL = Image.open(io.BytesIO(base64.b64decode(message['data'].split(',')[1])))
    image_np = np.array(image_PIL)
    plt.imshow(image_np)
    plt.show()
    print("no cześć")
    # imagefile = flask.request.files.get('imagefile', '')
    # return


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


if __name__ == '__main__':
    socketio.run(app, debug=True)
