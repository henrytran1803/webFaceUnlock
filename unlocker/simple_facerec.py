

from unlocker.models import Images
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import face_recognition

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
        # Truy vấn dữ liệu từ model Django
        images_queryset = Images.objects.all()

        # Xử lý từng hình ảnh trong queryset
        for image_obj in images_queryset:
            image_data = image_obj.image
            name = image_obj.id

            # Chuyển đổi dữ liệu nhị phân sang đối tượng Image
            image = Image.open(BytesIO(image_data))

            # Xử lý hình ảnh và tên theo cách cần thiết
            self.process_image(image, name)

        # Đóng kết nối cơ sở dữ liệu Django
        # Không cần đóng vì Django sẽ tự quản lý kết nối

        # In ra thông điệp
        print("Encodings loaded from Django database")


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
        # Find all the faces and face encodings in the current frame of video
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        # Convert to numpy array to adjust coordinates with frame resizing quickly
        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names
