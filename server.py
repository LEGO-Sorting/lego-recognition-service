import base64
import cv2
from random import random
from threading import Thread, Event

from flask import Flask, render_template, request, jsonify
from PIL import Image
from flask_socketio import SocketIO
from dto.NewPicture import NewPicture
from flask_cors import CORS, cross_origin
from lego_classifier_model import load_model, evaluate
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app)

# random number Generator Thread
thread = Thread()
thread_stop_event = Event()

model = load_model('04 Dec 2020 11 08 40.model', 'ohe.pickle')


def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    # infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random() * 10, 3)
        print(number)
        socketio.emit('new_picture', {'number': number}, namespace='/test')
        socketio.sleep(5)


def emit_image(body):
    print('emitting image: ' + body.category)
    socketio.emit('new_picture', {'category': body.category, 'image': body.image, 'content_type': body.content_type},
                  namespace='/test')
    socketio.sleep(1)


@app.route("/true", methods=["GET"])
def test_true():
    return jsonify(result=True)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predict", methods=["POST"])
def predict_brick():
    file = request.files['image']
    img_name = request.form.get('name')
    img_data = file.stream.read()
    img_data_encoded = base64.b64encode(img_data)
    img_content_type = file.content_type

    # TODO use model. Assumption for now category=img_name
    
    if isinstance(img_data, bytes):
        img_np_array = np.fromstring(img_data, np.uint8)
        img_np_array = cv2.imdecode(img_np_array, cv2.IMREAD_COLOR)

    else:
        img_np_array = np.array(img_data)

    img_category = evaluate(model, img_np_array)

    new_picture_command = NewPicture(img_category, img_data_encoded, img_content_type)
    handle_picture_received(new_picture_command)

    return jsonify({'msg': 'success'})


def handle_picture_received(body):
    print('Handle run')
    global thread

    if not thread.is_alive():
        thread = socketio.start_background_task(emit_image(body))
    # socketio.emit("new_picture", body, namespace='/test')


@socketio.on('connect', namespace='/test')
def test_connect():
    # TODO use load_model() to run thread with model
    print('Client connected')


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    # app.run(host="localhost", port=5002, debug=True)
    socketio.run(app, port=5002)
