# webFaceUnlock
## cách cài đặt clone Repo về
### Hệ điều hành MACOS 
- cd đường dẫn đến project
- source env/bin/active
- chạy python manage.py runserver
### Hệ điều hành window
- Xóa folder env
  - cd đến đường dẫn project
- chạy python3 -m venv env
-  pip install -r requirement.txt đợi tải thư viện 
- env/Scripts/Activate
- chạy python manage.py runserver
## mô tả cách hoạt động
- vào web như bth
- nếu như giữ khuông mặt trong khung ảnh quá 3s nó sẽ tự động chuyển trang
  - chưa có dữ liệu sẽ chuyển đến trang mượn tủ
    - có danh sách các tủ chưa được mượn
    - xác nhận tủ mượn sẽ tiếp tục chuyển đến trang mới
    - trang email cho người dùng nhập email nếu có trường hợp khách muốn nhận thông tin khi gần đến giwof đóng cửa mà quên chưa lấy 
    - quay lại trang chủ tự động
  - nếu đã có dữ liệu sẽ sang trang trả tủ 
    - trả tủ luôn trả xong xóa khỏi danh sách
    - mở tạm thời thì chỉ là muốn mở để lấy đồ rồi mượn tiếp nên không xóa
    - quay lại trang chủ
## Thư viện
- OpenCV
- Django 
- Celery
- Face-rec
- base 64
- sử dựng sqlite
- đây là những thứ chính
