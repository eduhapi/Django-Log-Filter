# logviewer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.filter_logs, name='filter_logs'),
]
