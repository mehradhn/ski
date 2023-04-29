# Register your models here.
from django.contrib import admin
from .models import Speciality, Doctor, Patient, TimeSlot, WeeklySchedule, Appointment
from django_jalali.admin.filters import JDateFieldListFilter

import django_jalali.admin as jadmin

class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number')

class WeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'doctor', 'display_time_slots')
    group_by = ['doctor', 'day_of_week']

    def display_time_slots(self, obj):
        return ', '.join(f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}" for slot in obj.time_slots.all())

    display_time_slots.short_description = 'شیفت ها'
   
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'first_name', 'last_name','medical_education_number','speciality',)
    list_filter = ('speciality',)
    
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    readonly_fields = ('tracking_number',)
    list_display = ('patient', 'doctor', 'day', 'time_slot', 'tracking_number')
    list_filter = ('doctor', )
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name', 'day')


admin.site.register(Speciality)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(TimeSlot)
admin.site.register(WeeklySchedule, WeeklyScheduleAdmin)