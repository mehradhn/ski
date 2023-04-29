from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError
import uuid
from django_jalali.db import models as jmodels
from django.db import models
from django.utils import timezone

class Speciality(models.Model):
    name = models.CharField(max_length=100, verbose_name="نوع تخصص", unique=True)
    
    class Meta:
        verbose_name = "تخصص"
        verbose_name_plural = "تخصص"

    def __str__(self):
        return f"{self.name}"

class Doctor(models.Model):
    first_name = models.CharField(max_length=100, verbose_name = "نام")
    last_name = models.CharField(max_length=100, verbose_name = "نام خانوادگی")
    medical_education_number = models.CharField(max_length=50, verbose_name = "شماره نظام پزشکی")
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name = "عکس")
    address = models.CharField(max_length=200, verbose_name = "آدرس")
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, verbose_name = "نوع تخصص")
    
    class Meta:
        verbose_name = "دکتر"
        verbose_name_plural = "دکتر ها"
    
    def image_tag(self):
        return format_html("<img width=100 src='{}'>".format(self.image.url))
    
    image_tag.short_description = 'عکس'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Patient(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    phone_number = models.CharField(max_length=15, verbose_name="تلفن همراه")
    class Meta:
        verbose_name = "بیمار"
        verbose_name_plural = "بیماران"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TimeInputWithoutSeconds(forms.TimeInput):
    input_type = 'time'

class TimeFieldWithoutSeconds(models.TimeField):
    def formfield(self, **kwargs):
        defaults = {'widget': TimeInputWithoutSeconds}
        defaults.update(kwargs)
        return super().formfield(**defaults)




class TimeInputWithoutSeconds(forms.TimeInput):
    input_type = 'time'
    format = '%H:%M'


class TimeFieldWithoutSeconds(models.TimeField):
    def formfield(self, **kwargs):
        defaults = {'widget': TimeInputWithoutSeconds}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class TimeSlot(models.Model):
    start_time = TimeFieldWithoutSeconds(verbose_name="ساعت شروع")
    end_time = TimeFieldWithoutSeconds(verbose_name="ساعت پایان")

    class Meta:
        verbose_name = "شیفت"
        verbose_name_plural = "شیفت ها"

    def duration(self):
        start_datetime = timezone.now().replace(hour=self.start_time.hour, minute=self.start_time.minute, second=0, microsecond=0)
        end_datetime = timezone.now().replace(hour=self.end_time.hour, minute=self.end_time.minute, second=0, microsecond=0)
        duration = (end_datetime - start_datetime).seconds // 60
        return duration
    

    def save(self, *args, **kwargs):
        if self.duration() != 30:
            raise ValueError("مدت زمان هر نوبت نیم ساعت میباشد")
        super().save(*args, **kwargs)

    def clean(self):
        if self.duration() != 30:
            raise ValidationError("مدت زمان هر نوبت نیم ساعت میباشد")

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"





class WeeklySchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,verbose_name="دکتر")
    day_of_week = models.PositiveSmallIntegerField(choices=[(i, _(day)) for i, day in enumerate(('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'))],verbose_name="روز")
    time_slots = models.ManyToManyField(TimeSlot, verbose_name="شیفت")

    class Meta:
        verbose_name = 'برنامه هفتگی'
        verbose_name_plural = 'برنامه هفتگی'
        unique_together = ['doctor', 'day_of_week']
        




class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="نام دکتر")
    day = models.PositiveSmallIntegerField(choices=[(i, _(day)) for i, day in enumerate(('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'))],verbose_name="روز")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="نام بیمار")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name="شیفت")
    tracking_number = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, verbose_name="کد رهگیری")

    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت ها"

    def clean(self):
        # Check if the patient has another appointment at the same time
        patient_appointments = Appointment.objects.filter(
            patient=self.patient,
            day=self.day,
            time_slot__start_time__lte=self.time_slot.start_time,
            time_slot__end_time__gt=self.time_slot.start_time,
        )
        if patient_appointments.exists():
            raise ValidationError(_("این بیمار در این زمان یک وقت ویزیت دارد"))

        # Check if another patient has an appointment with the same doctor at the same time
        doctor_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            day=self.day,
            time_slot__start_time__lte=self.time_slot.start_time,
            time_slot__end_time__gt=self.time_slot.start_time,
        ).exclude(pk=self.pk)
        if doctor_appointments.exists():
            raise ValidationError(_("یک بیمار دیگر در این زمان ویزیت با این دکتر دارد"))

        # Check if the patient has an appointment with another doctor at the same time
        other_doctor_appointments = Appointment.objects.filter(
            patient=self.patient,
            day=self.day,
            time_slot__start_time__lte=self.time_slot.start_time,
            time_slot__end_time__gt=self.time_slot.start_time,
        ).exclude(doctor=self.doctor)

        if other_doctor_appointments.exists():
            raise ValidationError(_("این بیمار در این زمان یک وقت ویزیت با دکتر دیگری دارد"))

        # Check for overlapping time slots with existing appointments
        overlapping_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            day=self.day,
        ).exclude(pk=self.pk).filter(
            time_slot__start_time__lt=self.time_slot.end_time,
            time_slot__end_time__gt=self.time_slot.start_time
        )

        if overlapping_appointments.exists():
            raise ValidationError(_("تداخل زمانی وجود دارد"))
        


    def __str__(self):
        return f"{self.patient} با {self.doctor} در  ساعت {self.time_slot.start_time.strftime('%H:%M')} - {self.time_slot.end_time.strftime('%H:%M') }"