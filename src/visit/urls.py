from django.urls import path
from . import views


urlpatterns= [
    path('home', views.main_view, name="main_view"),
    path('time-slots-json/', views.get_json_time_slot_data, name="time-slots-json"),
    path('speciality-json/', views.get_json_speciality_data, name="speciality-json"),
    path('doctor-json/<int:speciality_id>/', views.get_json_doctor_data, name="doctor-json"),
    path('schedule-json/<int:doctor_id>/', views.get_json_schedule, name="schedule-json"),
    path('create/', views.create_appointment, name="create"),
    path('schedules/', views.get_json_schedule_data, name="schedules"),
    path("track-number/", views.track_number, name='track-number'),
    path('appointments-data/', views.get_json_appointments_data, name="appointments-data"),
]

