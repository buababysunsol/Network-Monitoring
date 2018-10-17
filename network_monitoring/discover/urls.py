from django.urls import path
from django.views.generic.base import RedirectView, ContextMixin
from . import views, device_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('scan/network/', views.scanning_ip, name='scan-ip'),
    path('add/network/', views.add_database, name='add-ip'),
    path('views/', views.views_ip, name='view_all_ip'),
    path('add/', views.add_ip, name='add'),
    path('remove/', views.remove_ip, name='remove'),
    path('add/devices/', views.main, name='add-devices'),
    path('add/dis/devices', views.main, name='scan'),
    path('<str:node_ip>/view', device_views.view, name='node-view'),

    path('<str:node_ip>/edit', device_views.edit, name='node-edit'),
    path('<str:node_ip>/destroy', device_views.destroy, name='node-destroy')
]
