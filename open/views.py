
from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Images
import base64

def open(request):
    obj_ids = list(Images.objects.values_list('id', flat=True))
    print(obj_ids)
    value = 20
    button_names = [number for number in range(1, value + 1) if number not in obj_ids]
    button_groups = [button_names[i:i + 4] for i in range(0, len(button_names), 4)]
    context = {'button_groups': button_groups}
    return render(request, 'open/open.html', context)

def close(request):
    return render(request, 'open/close.html')

def email(request):
    return render(request, 'open/email.html')


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