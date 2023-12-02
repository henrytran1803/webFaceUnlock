from idlelib import window
from tkinter import Image
from unlocker.simple_facerec import SimpleFacerec
from unlocker.models import Images
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from django.shortcuts import redirect

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.sfr = SimpleFacerec()
        self.sfr.load_encoding_images_from_db()
        self.face_detected_time = None
        self.redirect_flag = False

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        face_locations, face_names = self.sfr.detect_known_faces(frame)

        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            self.fancyDraw(frame, (x1, y1, x2 - x1, y2 - y1))

        if face_names:
            if self.face_detected_time is None:
                self.face_detected_time = datetime.now()
            else:
                time_difference = datetime.now() - self.face_detected_time
                if time_difference.total_seconds() > 5:
                    # Set the redirect flag if a known face is detected for more than 5 seconds
                    self.redirect_flag = True
        else:
            # Reset the face detected time if no face is detected
            self.face_detected_time = None
            self.redirect_flag = False

        if self.face_detected_time is not None:
            time_difference = datetime.now() - self.face_detected_time
            if time_difference.total_seconds() > 5:
                # Set the redirect flag if an unknown face is detected for more than 5 seconds
                self.redirect_flag = True

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a format suitable for Tkinter
        _, jpeg = cv2.imencode('.jpg', frame_rgb)
        return jpeg.tobytes()
    def get_frames(self):
        while True:
            yield self.get_frame()
    def fancyDraw(self, img, bbox, l=30, t=5, rt=1):
        x, y, w, h = bbox
        x1, y1 = x + w, y + h

        cv2.rectangle(img, bbox, (255, 0, 255), rt)
        # Top Left  x,y
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


class LiveWebCam(object):
    def __init__(self):
        self.url = cv2.VideoCapture("rtsp://admin:88888888h@192.168.1.215:554/")

    def __del__(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        success, imgNp = self.url.read()
        resize = cv2.resize(imgNp, (640, 480), interpolation=cv2.INTER_LINEAR)
        ret, jpeg = cv2.imencode('.jpg', resize)
        return jpeg.tobytes()

class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        # Resize frame for a faster speed
        self.frame_resizing = 0.25

    # def load_encoding_images(self, images_path):
    #     # Load Images
    #     images_path = glob.glob(os.path.join(images_path, "*.*"))
    #


    #     print("{} encoding images found.".format(len(images_path)))
    #
    #     # Store image encoding and names
    #     for img_path in images_path:
    #         img = cv2.imread(img_path)
    #         rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #
    #         # Get the filename only from the initial file path.
    #         basename = os.path.basename(img_path)
    #         (filename, ext) = os.path.splitext(basename)
    #         # Get encoding
    #         img_encoding = face_recognition.face_encodings(rgb_img)[0]
    #
    #         # Store file name and file encoding
    #         self.known_face_encodings.append(img_encoding)
    #         self.known_face_names.append(filename)
    #     print("Encoding images loaded")
    def load_encoding_images_from_db(self):
        images_data = Images.objects.all()

        for image in images_data:
            image_array = np.frombuffer(image.image, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get encoding
            img_encoding = face_recognition.face_encodings(rgb_img)[0]

            # Convert image.id to a string
            image_id_str = str(image.id)

            # Store name and encoding
            self.known_face_encodings.append(img_encoding)
            self.known_face_names.append(image_id_str)
            print(image_id_str)

        print("Encodings loaded from database")
    def save_encodings_to_text(self, filename="face_encodings.txt"):
        with open(filename, "w") as file:
            for name, encoding in zip(self.known_face_names, self.known_face_encodings):
                file.write(f"{name}: {encoding}\n")
        print(f"Face encodings saved to {filename}")

    def load_encodings_from_text(self, filename="face_encodings.txt"):
        with open(filename, "r") as file:
            lines = file.readlines()

        for line in lines:
            name, encoding_str = line.strip().split(": ")
            encoding = np.fromstring(encoding_str[1:-1], dtype=float, sep=',')
            self.known_face_names.append(name)
            self.known_face_encodings.append(encoding)

        print(f"Face encodings loaded from {filename}")

    def detect_known_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)

        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)

        if not face_locations:
            return np.array([]), []

        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

            if any(face_distances):
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names