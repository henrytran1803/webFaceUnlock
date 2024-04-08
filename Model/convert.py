import os
from PIL import Image

# Đường dẫn đến thư mục chứa ảnh ban đầu
input_folder = "/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/Data/Trường"
# Đường dẫn đến thư mục lưu trữ ảnh đã chuyển kích thước
output_folder = "/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/Data/Trường2"

# Tạo thư mục đầu ra nếu nó chưa tồn tại
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Duyệt qua tất cả các file trong thư mục đầu vào
for filename in os.listdir(input_folder):
    # Kiểm tra xem file có phải là file ảnh hay không
    if filename.endswith(".jpg") or filename.endswith(".png"):
        # Đường dẫn đầy đủ đến file ảnh đầu vào
        input_path = os.path.join(input_folder, filename)
        # Đường dẫn đầy đủ đến file ảnh đầu ra
        output_path = os.path.join(output_folder, filename)

        # Mở ảnh sử dụng PIL
        image = Image.open(input_path)
        # Chuyển đổi kích thước ảnh thành 32x32
        resized_image = image.resize((32, 32))
        # Lưu ảnh đã chuyển kích thước
        resized_image.save(output_path)

print("Chuyển đổi kích thước ảnh thành công!")
