import urllib
import os
import cv2
import numpy as np

from Model.model import CreateModel

input_image_shape = (200, 200, 1)
num_classes = 3

model = CreateModel(input_image_shape, num_classes)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

filepath = '/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/Weights/weights.h5'
model.load_weights(filepath)

class_names = {0: 'Viet Anh', 1: 'Dien', 2: 'Truong'}

image_path = '/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/IMG_0825.JPG'

img = cv2.imread(image_path)


def preprocess_frame(frame):
    if len(frame.shape) == 2:
        gray_frame = frame
    else:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame_resized = cv2.resize(gray_frame, (200, 200), interpolation=cv2.INTER_AREA)
    frame_array = frame_resized.reshape(input_image_shape)
    frame_array = frame_array.astype('float32') / 255
    frame_array = np.expand_dims(frame_array, axis=0)
    return frame_array

processed_image = preprocess_frame(img)

prediction = model.predict(processed_image)
class_id = np.argmax(prediction, axis=1)[0]
class_name = class_names[class_id]

print("Predicted class:", class_name)
