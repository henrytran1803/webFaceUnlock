# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Images  # Adjust import based on your model

@shared_task
def send_reminder_emails():
    current_time = timezone.now().time()

    # Check if it's 10:30 PM
    if current_time.hour == 22 and current_time.minute == 30:
        # Get all Image objects with non-empty email fields
        images_with_emails = Images.objects.exclude(email='')

        for image in images_with_emails:
            # Send reminder email for each object
            send_mail('Cảnh báo', 'sắp đến giờ đóng của quý khách vui lòng lấy tư trang tại tủ', 'from@example.com', [image.email])
