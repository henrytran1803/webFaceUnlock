from django.urls import path, include
from unlocker import views


urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.video_feedrtps, name='video_feed'),
	path('livecam_feed', views.livecam_feed, name='livecam_feed'),
    path('capture_frame/', views.capture_frame, name='capture_frame'),
    path('check_redirect/', views.check_redirect, name='check_redirect'),
    path('save_unlock/', views.save_unlock, name='save_unlock'),
    ]