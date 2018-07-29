from django.urls import path
from . import views

urlpatterns = [
    path('network/', views.discover_network, name='discover-ip'),
    path('scan/network/', views.scanning_ip, name='scan-ip'),
]
