from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/launch/', views.launch_lab, name='launch_lab'),
    path('api/stop/', views.stop_lab, name='stop_lab'),
    path('api/status/<str:container_id>/', views.container_status, name='container_status'),
    path('api/reset/', views.reset_lab, name='reset_lab'),
]