# webFaceUnlock
---
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
---
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
---
##Các views
- Trang chủ.
- Chọn phòng.
- Trả phòng.
- Lựa chọn nhận thông báo (email).
---
##Model
```python
class Images(models.Model):
    name = models.TextField()
    image = models.BinaryField()
    email = models.EmailField(blank=True, null=True)  # Add this line
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images'
```
---

##Các urls
```python
#url open
urlpatterns = [
    path('', views.open, name='open'),
    path('close/', views.close, name='close'),
    path('process_form/', views.process_form, name='process_form'),
    path('email/', views.email, name='email'),
    path('borrow/', views.borrow, name='borrow'),
    path('collect_email/', views.associate_email, name='collect_email'),
    ]
#url unlocker
urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.video_feed, name='video_feed'),
	path('livecam_feed', views.livecam_feed, name='livecam_feed'),
    path('capture_frame/', views.capture_frame, name='capture_frame'),
    path('check_redirect/', views.check_redirect, name='check_redirect'),
    path('save_unlock/', views.save_unlock, name='save_unlock'),
    ]
```
---
##Các module xử lý views
- Xử ý việc mở cách thẻ html hiển thị giao diện
```python
def index(request):
    context = {'button_range': range(1, 21)}
    return render(request, 'unlocker/index.html', context)

def open():
    return redirect('open')

def close(request):
    return render(request, 'open/close.html')

def email(request):
    return render(request, 'open/email.html')
## Open ở đây sẽ lấy toàn bộ id người dùng vì khi mượn id người dùng sẽ là số tủ mượn
# nên load toàn bộ id người nhận
# và mình đang cho là có 20 tủ 
# viết ra lệnh lấy toàn bộ số trừ các id đã có rồi
# chia theo group là để xử lý bên html cho đẹp
def open(request):
    obj_ids = list(Images.objects.values_list('id', flat=True))
    print(obj_ids)
    value = 20
    button_names = [number for number in range(1, value + 1) if number not in obj_ids]
    button_groups = [button_names[i:i + 4] for i in range(0, len(button_names), 4)]
    context = {'button_groups': button_groups}
    return render(request, 'open/open.html', context)
```
- Xử lý chiếu trực tiếp video từ webcam
```python
# Hàm gen(camera) (Generator Function):
# Chức năng này là một generator function, thường được sử dụng để tạo ra một chuỗi giá trị theo thời gian.
# Hàm này nhận một đối tượng camera làm tham số đầu vào.
# Trong vòng lặp vô hạn, nó lấy khung hình hiện tại từ camera, lưu nó vào biến current_frame, và gán giá trị của current_frame cho biến toàn cục frame.
# Cập nhật giá trị của facename từ thuộc tính facename của camera.
def gen(camera):
    global stop_stream, facename, frame
    while True:
        current_frame = camera.get_frame()
        frame = current_frame
        facename = camera.facename
        if camera.redirect_flag:
            stop_stream = True
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n\r\n')
# Hàm video_feed(request) (View Function):
# Hàm này là một view function của Django, được sử dụng để xử lý yêu cầu và trả về phản hồi.
# Hàm trả về một StreamingHttpResponse sử dụng generator function gen(VideoCamera()) như là nguồn dữ liệu video.
# Kiểu nội dung được thiết lập là 'multipart/x-mixed-replace' để hỗ trợ hiển thị video theo thời gian thực.
def video_feed(request):
    global stop_stream, facename,frame
    frame = None
    facename ='unknown'
    stop_stream = False
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
```
- Views kiểm tra chuyển trang
```python
# Views kiểm tra chuyển trang lây một hình ảnh hiện tại từ video
# frame ở dạng byte muốn lưu vào session để có thể xử lý về sau
# Và nếu xác nhận một khuông mặt tồn tại trong khung hình quá 5s thì mới dám chắc khách hàng muốn nên sẽ xử lý
# Lấy tên xử lý 
# Có tên khác Unknown là khách hàng đã thuê
# Còn lại là chưa thuê
def check_redirect(request):
    if frame is not None:
        frame_base64 = base64.b64encode(frame).decode('utf-8')
        request.session['facename'] = facename
        request.session['face'] = frame_base64
        if stop_stream:
            facename_value = facename[0] if facename else 'Unknown'
            return JsonResponse({'redirect': True, 'facename': facename_value})
        else:
            facename_value = facename[0] if facename else 'Unknown'
            return JsonResponse({'redirect': False, 'facename': facename_value})
    else:
        return JsonResponse({'error': 'Frame is None'})
```
- Js xử lý việc ngắt streamhttps và chuyển sang trang
```js
    function checkRedirect() {
        $.ajax({
            url: '{% url "check_redirect" %}',
            success: function(data) {
                if (data.error) {
                    console.error(data.error);
                } else {
                    if (data.redirect) {
                        if (data.facename.toUpperCase() === 'UNKNOWN') {
                            window.location.href = '/open/';
                        } else {

                            window.location.href = '/open/close/';
                        }
                    }
                }
            }
        });
    }
```
- Views mượn tủ
```python
# Đầu tiên tôi sẽ lấy ảnh ở session lưu ở views chuyển hướng
# bắt sự kiện nếu người dùng nhấn một nút số tủ bất kỳ
# lấy id tủ chuyển frame sang byte lưu vào db 
# với 2 tham số là id và ảnh khuôn mặt
# Chuyển hướng đến views email
def borrow(request):
    frame_str = request.session.get('face', None)

    if frame_str:
        try:
            if request.method == 'POST':
                button_id = request.POST.get('button_id', None)

                frame_bytes = base64.b64decode(frame_str)

                Images.objects.create(id=button_id, image=frame_bytes)

                request.session['button'] = button_id

                return redirect('email')
            else:
                return HttpResponse("Invalid request method.")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")
    else:
        return HttpResponse("No face data in the session.")
```
- Views nhận email thông báo
```python
def associate_email(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        button_id = request.session.get('button', None)
        action = request.POST.get('action')

        if action == 'notify':
            if button_id is not None:
                try:
                    image_object = Images.objects.get(id=button_id)
                    image_object.email = email
                    image_object.save()

                    return redirect('index')
                except Images.DoesNotExist:
                    return HttpResponse('Object not found.')

        elif action == 'no_thanks':
            return redirect('index')

    return redirect('index')
```


```
```


---