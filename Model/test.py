import cv2
import numpy as np
from keras.models import load_model

# Load mô hình đã huấn luyện
model = load_model('face_recognition_model.h5')

# Khởi tạo video camera
cap = cv2.VideoCapture(0)

while True:
    # Đọc khung hình từ video camera
    ret, frame = cap.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_frame = cv2.resize(frame, (100, 100))
    preprocessed_frame = resized_frame / 255.0
    preprocessed_frame = np.expand_dims(preprocessed_frame, axis=0)

    # Dự đoán nhãn của hình ảnh
    prediction = model.predict(preprocessed_frame)
    predicted_class = np.argmax(prediction)

    # Hiển thị kết quả lên video camera
    cv2.putText(frame, f'Predicted Class: {predicted_class}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Video Camera', frame)

    # Thoát khỏi vòng lặp khi nhấn 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
