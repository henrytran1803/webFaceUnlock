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
# chuyển hướng đến email thì đợi ghi nhận nút bấm từ email
# 2 trường hợp
# notifyme thì nó sẽ lấy id người trước đó sau đó thêm email chuyển về trang chủ
# còn nothanks thì chuyển về trang chủ
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
- views trả hoặc tiếp tục mượn
```python
# Tên được lấy ra là ở dạng mảng nên ví dụ 14 sẽ là [1,4]
# nên tôi có hàm để gộp mảng lại
# nhận sự kiện nếu như nhấn close trả tủ thì xóa obj đó khỏi db chuyển về trang chủ
# còn sự kiện open mở tủ tạm thời thì chuyển lại về trang chủ
def process_form(request):
    try:
        object_id = request.session['facename']
        print(type(object_id))
        idobj = integer_number(object_id)
        print(idobj)
    except KeyError:
        return redirect('index')

    obj = get_object_or_404(Images, id=idobj)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'close':
            if obj:
                obj.delete()
                print('đã xóa')
        elif action == 'open':
            print('khjoong xóa')
            return redirect('index')
    return redirect('index')
def integer_number(lst):
    total = 0
    for i in lst:
        total = total * 10 + int(i)
    return total
```
---
##Xử lý khuôn mặt
###Class video camera
VideoCamera:
Class này cung cấp các phương thức để chụp và xử lý video từ webcam.
Sử dụng thư viện OpenCV để chụp video và nhận diện khuôn mặt.
Hàm init khởi tạo đối tượng chụp video và nạp thông tin khuôn mặt đã biết từ cơ sở dữ liệu.
Hàm del giải phóng đối tượng chụp video.
Hàm get_frame chụp một khung hình từ webcam, phát hiện khuôn mặt và trả về khung hình với các bounding box và tên khuôn mặt.
Hàm fancyDraw vẽ một hộp trang trí xung quanh khuôn mặt được phát hiện.
Hàm get_frames cung cấp một generator liên tục chụp và trả về các khung hình.
```python
# Hàm __init__ khởi tạo đối tượng VideoCamera và nạp thông tin khuôn mặt đã biết từ cơ sở dữ liệu.
# Hàm này khởi tạo một đối tượng cv2.VideoCapture() để chụp video từ webcam. Sau đó, hàm này gọi hàm load_encoding_images_from_db() để nạp thông tin khuôn mặt đã biết từ cơ sở dữ liệu.
# Hàm __del__
# Hàm __del__ giải phóng đối tượng VideoCamera.
# Hàm này đóng đối tượng cv2.VideoCapture().
# Hàm get_frame
# Hàm get_frame chụp một khung hình từ webcam, phát hiện khuôn mặt và trả về khung hình với các bounding box và tên khuôn mặt.
# Hàm này sử dụng phương thức read() của đối tượng cv2.VideoCapture() để chụp một khung hình từ webcam. Sau đó, hàm này gọi hàm detect_known_faces() để phát hiện khuôn mặt trong khung hình. Cuối cùng, hàm này trả về khung hình với các bounding box và tên khuôn mặt.
# Hàm fancyDraw
# Hàm fancyDraw vẽ một hộp trang trí xung quanh khuôn mặt được phát hiện.
# Hàm này sử dụng các phương thức của thư viện cv2 để vẽ một hộp màu đỏ xung quanh các khuôn mặt được phát hiện.
# Hàm get_frames
# Hàm get_frames cung cấp một generator liên tục chụp và trả về các khung hình.
# Hàm này liên tục gọi hàm get_frame() và trả về khung hình được chụp.
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.sfr = SimpleFacerec()
        self.sfr.load_encoding_images_from_db()
        self.face_detected_time = None
        self.redirect_flag = False
        self.facename='unknown'
    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        face_locations, face_names = self.sfr.detect_known_faces(frame)
        self.facename = face_names
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
```
###Class SimpleFacerec
Phương thức __init__:
Khởi tạo một đối tượng SimpleFacerec.
known_face_encodings: Danh sách chứa các mã hóa khuôn mặt đã biết.
known_face_names: Danh sách chứa tên tương ứng với mã hóa khuôn mặt.
```python
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        # Resize frame for a faster speed
        self.frame_resizing = 0.25
```
Phương thức load_encoding_images_from_db:
Lấy các dữ liệu ảnh từ cơ sở dữ liệu (Images.objects.all()).
Đọc dữ liệu ảnh và chuyển đổi thành mảng numpy.
Sử dụng thư viện face_recognition để xác định vị trí khuôn mặt và mã hóa khuôn mặt.
Nếu có khuôn mặt được tìm thấy, thêm mã hóa khuôn mặt và tên tương ứng vào danh sách.
```python
   def load_encoding_images_from_db(self):
        images_data = Images.objects.all()
        for image in images_data:
            print(image.id)
            try:
                image_array = np.frombuffer(image.image, np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_img)
                if face_locations:
                    img_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
                    image_id_str = str(image.id)
                    self.known_face_encodings.append(img_encoding)
                    self.known_face_names.append(image_id_str)
                    print(f"Face encoding loaded for image ID: {image_id_str}")
                else:
                    print(f"No faces found in image ID: {image.id}")

            except Exception as e:
                print(f"Error processing image ID {image.id}: {e}")

        print("Encodings loaded from database")

        print("Encodings loaded from database")
```

Phương thức detect_known_faces:
Nhận một khung hình làm đối số đầu vào.
Giảm kích thước của khung hình để tăng tốc độ xử lý (cv2.resize).
Chuyển đổi khung hình thành định dạng màu RGB (cv2.cvtColor).
Sử dụng face_recognition để xác định vị trí và mã hóa khuôn mặt trong khung hình giảm kích thước.
So sánh mã hóa khuôn mặt với danh sách các mã hóa khuôn mặt đã biết.
Trả về vị trí khuôn mặt và tên tương ứng.
```python
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
```
##Đôi điều về thư viện face_recognition
Thư viện face_recognition là một giao diện đơn giản được xây dựng trên thư viện dự án mã nguồn mở dlib và được tạo ra bởi Adam Geitgey. Nó giúp đơn giản hóa quá trình nhận diện và mã hóa khuôn mặt, làm cho các nhiệm vụ nhận diện khuôn mặt trở nên dễ dàng hơn với Python.

Input của Thư Viện face_recognition:
Ảnh đầu vào: Đối với việc nhận diện khuôn mặt, bạn có thể sử dụng ảnh chụp từ camera hoặc tải ảnh từ các nguồn khác nhau. Thư viện hỗ trợ đa dạng định dạng ảnh (JPEG, PNG, ...).
Output của Thư Viện face_recognition:
Face Landmarks (Vị trí các điểm trên khuôn mặt):

face_recognition.face_landmarks(image): Trả về một danh sách chứa các điểm quan trọng trên khuôn mặt như mũi, mắt, miệng, ...
Face Locations (Vị trí của khuôn mặt):

face_recognition.face_locations(image): Trả về một danh sách các tuple (top, right, bottom, left) đại diện cho vị trí của các khuôn mặt trong ảnh.
Face Encodings (Mã hóa khuôn mặt):

face_recognition.face_encodings(image, face_locations): Trả về mã hóa khuôn mặt cho các khuôn mặt được định vị trong ảnh.
So Sánh Khuôn Mặt:

face_recognition.compare_faces(known_face_encodings, face_encoding): So sánh mã hóa khuôn mặt của một khuôn mặt với danh sách các mã hóa đã biết.
Khoảng Cách Giữa Các Khuôn Mặt:

face_recognition.face_distance(known_face_encodings, face_encoding): Tính toán khoảng cách giữa mã hóa khuôn mặt của một khuôn mặt và danh sách các mã hóa đã biết.

---
##Gửi lịch email
```python
#celery.py
# from __future__ import absolute_import, unicode_literals: Dòng này đảm bảo rằng Python 2 và Python 3 tương thích với nhau.
# import os: Dòng này import thư viện os để thực hiện các thao tác với hệ thống.
# from celery import Celery: Dòng này import thư viện Celery để sử dụng chức năng background task.
# Cài đặt Django settings module:
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webFaceUnlock.settings'): Dòng này đặt biến môi trường DJANGO_SETTINGS_MODULE thành webFaceUnlock.settings. Điều này cho phép Celery biết cài đặt nào của Django sẽ được sử dụng.
# Khởi tạo Celery instance:
# app = Celery('webFaceUnlock'): Dòng này tạo một instance Celery mới có tên webFaceUnlock.
# Cấu hình Celery:
# app.config_from_object('django.conf:settings', namespace='CELERY'): Dòng này cấu hình Celery bằng cách load các cài đặt của Django từ namespace CELERY.
# app.autodiscover_tasks(): Dòng này tự động khám phá và register các task được định nghĩa trong các app Django đã cài đặt.
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webFaceUnlock.settings')

app = Celery('webFaceUnlock')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
```


```python
#tasks.py
# 1. Import thư viện:
# from datetime import timezone: Import chức năng timezone từ thư viện datetime để lấy múi giờ hiện tại.
# from celery import shared_task: Import decorator shared_task từ thư viện celery để định nghĩa một task.
# from django.core.mail import send_mail: Import hàm send_mail từ thư viện django.core.mail để gửi email.
# from .models import Images: Import model Images từ ứng dụng hiện tại.
# 2. Định nghĩa task:
# @shared_task: Decorator này xác định hàm send_reminder_emails là một task của Celery.
# 3. Lấy thời gian hiện tại:
# current_time = timezone.now().time(): Lấy thời gian hiện tại theo định dạng time và lưu vào biến current_time.
# 4. Kiểm tra thời gian:
# if current_time.hour == 22 and current_time.minute == 30: Kiểm tra xem thời gian hiện tại có phải là 10:30 PM (giờ đóng cửa) hay không.
# 5. Lấy danh sách email:
# images_with_emails = Images.objects.exclude(email=''): Lấy tất cả các đối tượng Images có email không rỗng.
# 6. Vòng lặp gửi email:
# for image in images_with_emails: Duyệt qua từng đối tượng Images trong danh sách.
# send_mail('Cảnh báo', 'sắp đến giờ đóng cửa quý khách vui lòng lấy tư trang tại tủ', 'from@example.com', [image.email]): Gửi email cho người dùng với nội dung "sắp đến giờ đóng cửa quý khách vui lòng lấy tư trang tại tủ" đến địa chỉ email được lưu trong trường email của đối tượng Images.
# 7. Tóm tắt:
# Task này thực hiện các chức năng sau:
# Lấy thời gian hiện tại.
# Kiểm tra xem thời gian hiện tại có phải là 10:30 PM hay không.
# Nếu đúng, lấy tất cả các địa chỉ email có trong model Images.
# Gửi email nhắc nhở cho người dùng.
from datetime import timezone

from celery import shared_task
from django.core.mail import send_mail
from .models import Images

@shared_task
def send_reminder_emails():
    current_time = timezone.now().time()
    if current_time.hour == 22 and current_time.minute == 30:
        images_with_emails = Images.objects.exclude(email='')

        for image in images_with_emails:
            send_mail('Cảnh báo', 'sắp đến giờ đóng cửa quý khách vui lòng lấy tư trang tại tủ', 'from@example.com', [image.email])
```
```python
#settings.py
# 1. Broker và Result Backend:
# CELERY_BROKER_URL: Địa chỉ của broker sử dụng để truyền và nhận các message của Celery. Trong trường hợp này, Redis được sử dụng với địa chỉ localhost:6379/0.
# CELERY_RESULT_BACKEND: Địa chỉ của backend sử dụng để lưu trữ kết quả của các task. Redis cũng được sử dụng với cùng địa chỉ như broker.
# 2. Múi giờ:
# CELERY_TIMEZONE: Múi giờ được sử dụng để thực hiện các task. Trong trường hợp này, Asia/Ho_Chi_Minh được sử dụng.
# 3. Cấu hình email:
# EMAIL_BACKEND: Backend được sử dụng để gửi email. Trong trường hợp này, backend SMTP của Django được sử dụng.
# EMAIL_HOST: Địa chỉ của server SMTP.
# EMAIL_PORT: Cổng của server SMTP.
# EMAIL_USE_TLS: Sử dụng TLS để bảo mật khi gửi email.
# EMAIL_HOST_USER: Username của tài khoản email được sử dụng để gửi email.
# EMAIL_HOST_PASSWORD: Password của tài khoản email được sử dụng để gửi email.
# 4. Celery Beat Schedule:
# CELERY_BEAT_SCHEDULE: Cấu hình để chạy task theo chu kỳ.
# 'send-reminder-emails': Tên của task.
# 'task': Đường dẫn đến task.
# 'schedule': Chu kỳ chạy task. Trong trường hợp này, task sẽ chạy vào lúc 22:30 hàng ngày.

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tranvietanh1803@gmail.com'
EMAIL_HOST_PASSWORD = 'nawh nonv shpj olkl'
CELERY_BEAT_SCHEDULE = {
    'send-reminder-emails': {
        'task': 'webFaceUnlock.unlocker.tasks.send_reminder_emails',
        'schedule': crontab(hour=22, minute=30),
    },
}
```