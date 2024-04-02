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

def load_known_face_ids(file_path):
    with open(file_path, 'r') as file:
        known_face_ids = [line.strip() for line in file]
    return set(known_face_ids)

# Lớp detectmodel
class detectmodel(object):
    def __init__(self, url):
        self.url = url
        self.images_data = load_known_face_ids('/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/known_face_ids.txt')
        self.face_detected_time = None
        self.redirect_flag = False
        self.facename = 'unknown'
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def get_frame_from_url(self):
        img_resp = urllib.request.urlopen(self.url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)
        return frame

    def preprocess_frame(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_resized = cv2.resize(gray_frame, (200, 200), interpolation=cv2.INTER_AREA)
        frame_array = frame_resized.reshape(input_image_shape)
        frame_array = frame_array.astype('float32') / 255
        frame_array = np.expand_dims(frame_array, axis=0)
        return frame_array

    def detect_faces(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=9)
        return faces

    def fancyDraw(self, img, bbox, l=30, t=5, rt=1):
        x, y, w, h = bbox
        x1, y1 = x + w, y + h

        cv2.rectangle(img, bbox, (255, 0, 255), rt)

        cv2.line(img, (x, y), (x + l, y), (255, 0, 255), t)
        cv2.line(img, (x, y), (x, y + l), (255, 0, 255), t)
        # Top Right  x1,y
        cv2.line(img, (x1, y), (x1 - l, y), (255, 0, 255), t)
        cv2.line(img, (x1, y), (x1, y + l), (255, 0, 255), t)
        # Bottom Left  x,y1
        cv2.line(img, (x, y1), (x + l, y1), (255, 0, 255), t)
        cv2.line(img, (x, y1), (x, y1 - l), (255, 0, 255), t)
        # Bottom Right  x1,y1
        cv2.line(img, (x1, y1), (x1 - l, y1), (255, 0, 255), t)
        cv2.line(img, (x1, y1), (x1, y1 - l), (255, 0, 255), t)
        return img

    def detect_known_faces(self, frame):
        detections = self.detect_faces(frame)
        faces = []
        face_names = []

        for detection in detections:
            x, y, width, height = detection
            x, y = max(0, x), max(0, y)
            face_frame = frame[y:y + height, x:x + width]
            face_image = self.preprocess_frame(face_frame)

            prediction = model.predict(face_image)
            class_id = np.argmax(prediction, axis=1)[0]

            if str(class_id) in self.images_data:
                face_name = class_names.get(class_id, "Unknown")
            else:
                face_name = "Unknown"

            faces.append((x, y, width, height))
            face_names.append(face_name)

        return faces, face_names

    def detect_faces_and_classify(self):
        while True:
            frame = self.get_frame_from_url()
            face_locations, face_names = self.detect_known_faces(frame)

            for ((x, y, w, h), name) in zip(face_locations, face_names):
                text_y = y - 10 if y - 10 > 30 else y + 10
                cv2.putText(frame, name, (x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                frame = self.fancyDraw(frame, (x, y, w, h))

            cv2.imshow('Realtime Face Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

url = 'http://192.168.1.23/cam.jpg'
detector = detectmodel(url)
detector.detect_faces_and_classify()
