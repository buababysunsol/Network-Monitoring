from django.urls import path
from . import views

urlpatterns = [
    path('network/', views.discover_network),
]
