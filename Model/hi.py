# import cv2
# import urllib.request
# import numpy as np
#
# url = 'http://192.168.1.23/cam-mid.jpg'
#
# def run1():
#     cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
#     while True:
#         try:
#             img_resp = urllib.request.urlopen(url)
#             imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
#             im = cv2.imdecode(imgnp, -1)
#
#             cv2.imshow('live transmission', im)
#             key = cv2.waitKey(5)
#             if key == ord('q'):
#                 break
#         except Exception as e:
#             print("Error:", e)
#             continue
#
#     cv2.destroyAllWindows()
#
# if __name__ == '__main__':
#     print("started")
#     run1()
import cv2
import requests
import numpy as np

image_url = 'http://192.168.1.23/cam.jpg'

face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

capture_face = False  # Flag to indicate if a face is detected for capture
capture_index = 0  # Index to track captured images

while True:
    response = requests.get(image_url)

    if response.status_code != 200:
        print("Failed to retrieve image from the URL. Exiting...")
        break

    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)

    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=9)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if capture_face:
                cv2.imwrite(f"/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/Image/images/captured_face_{capture_index}.jpg", img[y:y+h, x:x+w])
                print("Captured face saved.")
                capture_index += 1
                capture_face = False

        cv2.imshow('Stream', img)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key == 13:  # Check if Enter key is pressed
        capture_face = True

cv2.destroyAllWindows()

