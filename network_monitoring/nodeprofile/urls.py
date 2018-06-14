from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.view_all),
    path('<int:node_id>/', views.view_node),
    path('<str:oid>/easy/', views.view_node_easy)
]
