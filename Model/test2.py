import cv2
import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

from Model.model import CreateModel

input_image_shape = (200, 200, 1)
num_classes = 3

model = CreateModel(input_image_shape, num_classes)

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

filepath = 'Weights/weights.h5'
model.load_weights(filepath)

class_names = {0: 'Dien', 1: 'Dien', 2: 'Truong'}

def preprocess_frame(frame):
    frame_resized = cv2.resize(frame, (200, 200))
    frame_array = np.array(frame_resized).astype('float32')
    frame_array /= 255
    frame_array = np.expand_dims(frame_array, axis=0)
    return frame_array



def detect_faces_and_classify():
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_image = gray[y:y+h, x:x+w]
            face_image = preprocess_frame(face_image)

            predictions = model.predict(face_image)
            class_id = np.argmax(predictions)
            class_name = class_names[class_id]

            cv2.putText(frame, class_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('Realtime Face Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":


    detect_faces_and_classify()
