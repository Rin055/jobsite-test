from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/create/', views.job_create, name='job_create'),
    path('job/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('job/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('job/<int:pk>/apply/', views.apply_for_job, name='apply_for_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('job/<int:pk>/applications/', views.job_applications, name='job_applications'),
    path('application/<int:pk>/status/<str:status>/', views.update_application_status, name='update_application_status'),
]