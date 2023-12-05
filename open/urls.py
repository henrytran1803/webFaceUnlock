from django.urls import path, include
from open import views


urlpatterns = [
    path('', views.open, name='open'),
    path('close/', views.close, name='close'),
    path('process_form/', views.process_form, name='process_form'),
    path('email/', views.email, name='email'),
    path('borrow/', views.borrow, name='borrow'),
    path('collect_email/', views.associate_email, name='collect_email'),
    ]