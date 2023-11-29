from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from unlocker.camera import VideoCamera, LiveWebCam

from .models import Images
# Create your views here.


def index(request):
    return render(request, 'unlocker/index.html')
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def livecam_feed(request):
    return StreamingHttpResponse(gen(LiveWebCam()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def capture_frame(request):
    if request.method == 'POST':
        # Lấy tên ảnh từ form
        image_name = request.POST.get('textboxx', 'default_name')

        # Chụp frame từ camera
        camera = VideoCamera()
        frame = camera.get_frame()

        # Lưu frame vào cơ sở dữ liệu
        Images.objects.create(id=image_name, image=frame)

    return render(request, 'open/index.html')