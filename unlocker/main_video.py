import sqlite3

import cv2
import tkinter as tk
from tkinter import simpledialog
from simple_facerec import SimpleFacerec
from PIL import Image, ImageTk

def fancyDraw(img, bbox, l=30, t=5, rt=1):
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

class FaceRecognitionApp:
    def __init__(self):
        self.sfr = SimpleFacerec()
        self.sfr.load_encoding_images_from_db('../db.sqlite3')
        self.conn = sqlite3.connect('../db.sqlite3')
        self.cursor = self.conn.cursor()
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Error: Couldn't open camera.")
            exit()

        self.root = tk.Tk()
        self.root.title("Face Recognition")

        self.capture_button = tk.Button(self.root, text="Capture", command=self.capture_image)
        self.capture_button.pack()

        self.name_entry = tk.Entry(self.root, width=20)
        self.name_entry.pack()

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.show_video_feed()

    def show_video_feed(self):
        ret, frame = self.cap.read()

        # Detect Faces
        face_locations, face_names = self.sfr.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            fancyDraw(frame, (x1, y1, x2 - x1, y2 - y1))

        # Convert the frame to a format suitable for Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=image)

        self.video_label.config(image=img)
        self.video_label.image = img

        self.root.after(10, self.show_video_feed)

    def capture_image(self):
        ret, frame = self.cap.read()

        # Detect Faces
        face_locations, face_names = self.sfr.detect_known_faces(frame)

        if len(face_locations) == 1:
            name = simpledialog.askstring("Input", "Enter a name for the captured image:")
            if name:
                # Chuyển đổi ảnh sang định dạng BLOB
                img_encoded = cv2.imencode('.jpg', frame)[1]
                image_data = img_encoded.tobytes()

                # Thêm ảnh và tên ảnh vào cơ sở dữ liệu
                self.cursor.execute('INSERT INTO images (name, image) VALUES (?, ?)', (name, image_data))
                self.conn.commit()

                print(f"Captured image saved to database with name: {name}")

                # Load updated encodings after capturing an image
                self.sfr.load_encoding_images_from_db("image_database.db")

                # Clear the name entry
                self.name_entry.delete(0, tk.END)
        else:
            print("No face or multiple faces detected. Please capture a single face.")


    def run(self):
        self.root.mainloop()
        self.cap.release()

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.run()
