import os
import sqlite3
import cv2
from datetime import datetime

# # Kết nối đến cơ sở dữ liệu SQLite
# conn = sqlite3.connect('db.sqlite3')
# cursor = conn.cursor()
#
# # Tạo bảng để lưu trữ ảnh, tên ảnh, ID và thời gian cập nhật
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS images (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         image BLOB NOT NULL,
#         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#     )
# ''')
#
# # Commit các thay đổi và đóng kết nối
# conn.commit()
# conn.close()
def load_images_to_database(folder_path):
    # Kết nối đến cơ sở dữ liệu SQLite
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Lặp qua tất cả các file trong thư mục
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Đường dẫn đầy đủ của ảnh
            image_path = os.path.join(folder_path, filename)

            # Đọc ảnh từ file
            img = cv2.imread(image_path)

            # Chuyển đổi ảnh sang dạng BLOB
            img_encoded = cv2.imencode('.jpg', img)[1]
            image_data = img_encoded.tobytes()

            # Thêm ảnh, tên ảnh và thời gian vào cơ sở dữ liệu
            cursor.execute('INSERT INTO images (image ) VALUES (?)',
                           (image_data))

    # Commit các thay đổi và đóng kết nối
    conn.commit()
    conn.close()

image_folder_path = 'images'

# Load tất cả các ảnh từ thư mục vào cơ sở dữ liệu
load_images_to_database(image_folder_path)
