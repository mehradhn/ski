from django.urls import path
from . import views

urlpatterns= [
    path('', views.main_view, name="main_view"),
    path('speciality-json/', views.get_json_speciality_data, name="speciality-json"),
    path('doctor-json/<int:speciality_id>/', views.get_json_doctor_data, name="doctor-json"),
    path('schedule-json/<int:doctor_id>/', views.get_json_schedule, name="schedule-json"),
     path('create/', views.create_appointment, name='create_appointment'),
]