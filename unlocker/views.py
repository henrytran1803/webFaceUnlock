import base64
import gzip

from . import camera
from .models import Images
from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from .camera import VideoCamera
import cv2
stop_stream = False
facename='unknown'
frame = None
def index(request):
    context = {'button_range': range(1, 21)}
    return render(request, 'unlocker/index.html', context)

def open():
    return redirect('open')



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

def video_stream():
    global picture
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('rtsp://172.20.10.8:8554/mjpeg/1')

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # frame = cv2.resize(frame, (640, 480))

        _, jpeg = cv2.imencode('.jpg', frame)
        picture = jpeg
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

# View chứa hàm streaming
def video_feedrtps(request):
    return StreamingHttpResponse(video_stream(), content_type="multipart/x-mixed-replace;boundary=frame")

def video_feed(request):
    global stop_stream, facename,frame
    frame = None
    facename ='unknown'
    stop_stream = False
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

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

def livecam_feed(request):
    return redirect('open')

def capture_frame(request):
    if request.method == 'POST':
        image_name = request.POST.get('textboxx', 'default_name')
        camera = VideoCamera()
        frame = camera.get_frame()
        Images.objects.create(id=image_name, image=frame)
    return render(request, 'open/index.html')

def save_unlock(request):
    if request.method == 'POST':
        unlock_text = request.POST.get('textboxx', 'default_name')
        last_clicked_button = request.POST.get('last_clicked_button')
        print(last_clicked_button)
        return render(request, 'open/success.html', {'unlock_text': unlock_text})
    return render(request, 'open/index.html')
