# import cv2
# import os
#
# if __name__ == "__main__":
#
#     def create_directory(directory):
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#
#
#     create_directory('images')
#
#     faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#
#     cam = cv2.VideoCapture(0)
#
#     cam.set(3, 640)
#     cam.set(4, 480)
#
#     count = 0
#     face_id = input('\nEnter user id (MUST be an integer) and press <return> -->  ')
#     print("\n[INFO] Initializing face capture. Look at the camera and wait...")
#
#     while True:
#         ret, img = cam.read()
#
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#         faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
#
#         for (x, y, w, h) in faces:
#             cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
#
#             count += 1
#
#             cv2.imwrite(f"Model/Image/images/Users-{face_id}-{count}.jpg", gray[y:y + h, x:x + w])
#             cv2.imshow('image', img)
#
#         k = cv2.waitKey(300) & 0xff
#         if k == 27:
#             break
#
#         elif count >= 100:
#             break
#
#     print("\n[INFO]Success! Exiting Program.")
#
#     cam.release()
#
#     cv2.destroyAllWindows()
import cv2
import os
import numpy as np
import requests
from urllib3.exceptions import ProtocolError
import time

if __name__ == "__main__":
    def create_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    image_url = 'http://192.168.1.23/cam-mid.jpg'

    count = 0
    face_id = input('\nEnter user id (MUST be an integer) and press <return> -->  ')
    print("\n[INFO] Initializing face capture. Look at the camera and wait...")

    retry_count = 5
    while retry_count > 0:
        try:
            response = requests.get(image_url)
            img = cv2.imdecode(np.frombuffer(response.content, np.uint8), -1)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

                count += 1

                cv2.imwrite(f"/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/Image/images/Users-{face_id}-{count}.jpg", gray[y:y + h, x:x + w])
                cv2.imshow('image', img)

            k = cv2.waitKey(300) & 0xff
            if k == 27:
                break

            elif count >= 100:
                break

        except (ProtocolError, requests.exceptions.ChunkedEncodingError) as e:
            print(f"Error: {e}")
            retry_count -= 1
            time.sleep(1)  # Wait for 1 second before retrying

    print("\n[INFO]Success! Exiting Program.")

    cv2.destroyAllWindows()
