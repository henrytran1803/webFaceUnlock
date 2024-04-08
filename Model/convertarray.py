from PIL import Image
import numpy as np

# Đường dẫn đến bức ảnh
image_path = "/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/images/User-1-1.jpg"

# Đọc ảnh và chuyển đổi thành ảnh xám
image = Image.open(image_path).convert('L')


image = image.resize((32, 32))

# Chuyển đổi ảnh thành mảng numpy
image_array = np.array(image)

# Chuyển đổi mảng 2D thành mảng 1D
image_1d_array = image_array.flatten()

# Đường dẫn đến file để lưu mảng
output_file = "/Users/tranvietanh/PycharmProjects/webFaceUnlock/Model/known_face_ids.txt"

# Lưu mảng vào file văn bản
np.savetxt(output_file, image_1d_array)