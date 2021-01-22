from __future__ import print_function
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.engine.training import Model
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras import models
from typing import Tuple
import numpy as np
import pickle
import cv2
import sys


def load_model(model_path: str, ohe_path: str) -> Tuple[Model, OneHotEncoder]:
    model = models.load_model(model_path)
    ohe = pickle.load(open(ohe_path, "rb"))
    return model, ohe


def evaluate(model: Tuple[Model, OneHotEncoder], input_: np.ndarray):

    ohe = model[1]
    model = model[0]
    input_shape = model.input_shape[1:4]

    if input_.shape[0:2] != input_shape:
        input_ = cv2.resize(input_, (input_shape[1], input_shape[0]))

    if input_shape != input_.shape:
        print(f"Received shape of an input is {input_.shape} and expected shape is {input_shape}. \
Two first parameters {input_.shape[0:2]} where resized to fit a model \
so the problem is with the others{' ' + input_.shape[2:] if len(input_.shape[2:]) != 0 else ''}.", file=sys.stderr)
        exit(-1)

    input_ = input_.reshape((-1, *model.input_shape[1:]))
    
    keras_image_generator = ImageDataGenerator(
        rescale=1. / 255,
        samplewise_std_normalization=True,
        samplewise_center=True
    ).flow(input_, batch_size=len(input_), shuffle=False)
    input_ = keras_image_generator.next()

    prediction = model.predict(input_)
    prediction = ohe.inverse_transform(prediction)
    return prediction[0][0]
