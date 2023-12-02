
from .models import Images

from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from .camera import VideoCamera

stop_stream = False

def index(request):
    return render(request, 'unlocker/index.html')

def open():
    return redirect('open')

def gen(camera):
    global stop_stream
    while True:
        frame = camera.get_frame()
        if camera.redirect_flag:
            stop_stream = True
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    global stop_stream
    stop_stream = False
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def check_redirect(request):
    print(stop_stream)
    if stop_stream:
        return JsonResponse({'redirect': True})
    else:
        return JsonResponse({'redirect': False})

def run_parallel():
    with ThreadPoolExecutor() as executor:
        executor.submit(video_feed)
        executor.submit(check_redirect)

def livecam_feed(request):
    return redirect('open')


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