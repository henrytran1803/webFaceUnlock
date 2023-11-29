from django.urls import path, include
from open import views


urlpatterns = [
    path('', views.index, name='open'),
    ]