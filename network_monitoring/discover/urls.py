from django.urls import path
from . import views

urlpatterns = [
    path('network/', views.discover_network),
    path('scan/network/', views.scanning_ip),
]
