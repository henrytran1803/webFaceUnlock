import cv2
import os

if __name__ == "__main__":

    def create_directory(directory):
        """
        Create a directory if it doesn't exist.

        Parameters:
            directory (str): The path of the directory to be created.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)


    create_directory('images')

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)

    cam.set(3, 640)
    cam.set(4, 480)

    count = 0
    face_id = input('\nEnter user id (MUST be an integer) and press <return> -->  ')
    print("\n[INFO] Initializing face capture. Look at the camera and wait...")

    while True:
        ret, img = cam.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            count += 1

            face_img = gray[y:y + h, x:x + w]  # Cắt khuôn mặt từ ảnh xám
            resized_face = cv2.resize(face_img, (32, 32))  # Thay đổi kích thước hình ảnh khuôn mặt thành 32x32

            cv2.imwrite(f"./images/User-{face_id}-{count}.jpg", resized_face)

        k = cv2.waitKey(100) & 0xff
        if k == 27:
            break

        elif count >= 100:
            break

    print("\n[INFO]Success! Exiting Program.")

    cam.release()

    cv2.destroyAllWindows()