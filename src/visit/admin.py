# Register your models here.
from django.contrib import admin
from .models import Speciality, Doctor, Patient, TimeSlot, WeeklySchedule, Appointment
from django.http import HttpResponse



class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number')


class WeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'doctor', 'display_time_slots')

    def display_time_slots(self, obj):
        return ', '.join(f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}" for slot in obj.time_slots.all())

    display_time_slots.short_description = 'شیفت ها'
   
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'first_name', 'last_name', 'medical_education_number', 'speciality',)
    list_filter = ('speciality',)

    def export_as_pdf(self, request, queryset):
        # Generate the PDF file using the queryset
        pdf_file = generate_pdf(queryset)

        # Set the content-disposition header to force download the file
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="doctors.pdf"'
        return response

    export_as_pdf.short_description = "لیست پزشکان"

    actions = [export_as_pdf]
    
    
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









from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.platypus import Table, TableStyle, Image
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
import os
import io
def generate_pdf(queryset):
    # Create a file-like buffer to receive PDF data.
    pdfmetrics.registerFont(TTFont('tahoma', 'tahoma.ttf'))
    buffer = io.BytesIO()
    width, height = letter
    padding = 8
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)

    # Write some text to the PDF file
    p.setFont('tahoma', 12)
    reshaped_text = arabic_reshaper.reshape(" ")
    display_text = get_display(reshaped_text)
    p.drawString(100, 750 , display_text)

    # Add a table to the PDF file
    data = []

    reshaped_title_first_name = arabic_reshaper.reshape("نام")
    reordered_title_first_name = get_display(reshaped_title_first_name)


    reshaped_title_last_name = arabic_reshaper.reshape("نام خانوادگی")
    reordered_title_last_name = get_display(reshaped_title_last_name)


    reshaped_title_medical_education_number = arabic_reshaper.reshape("کد ن.پ")
    reordered_title_medical_education_number = get_display(reshaped_title_medical_education_number)


    reshaped_title_speciality = arabic_reshaper.reshape("تخصص")
    reordered_title_speciality = get_display(reshaped_title_speciality)

    reshaped_title_image = arabic_reshaper.reshape("عکس")
    reordered_title_image = get_display(reshaped_title_image)




    data.append([reordered_title_speciality, reordered_title_medical_education_number, reordered_title_last_name,  reordered_title_first_name, reordered_title_image]),
    for doctor in queryset:
        first_name = doctor.first_name
        last_name = doctor.last_name
        medical_education_number = doctor.medical_education_number
        speciality = doctor.speciality.name

        # Reshape and reorder the Arabic text
        reshaped_first_name = arabic_reshaper.reshape(first_name)
        reordered_first_name = get_display(reshaped_first_name)

        reshaped_last_name = arabic_reshaper.reshape(last_name)
        reordered_last_name = get_display(reshaped_last_name)


        reshaped_medical_education_number = arabic_reshaper.reshape(medical_education_number)
        reordered_medical_education_number = get_display(reshaped_medical_education_number)

        reshaped_speciality = arabic_reshaper.reshape(speciality)
        reordered_speciality = get_display(reshaped_speciality)

        image_path = os.path.join(settings.MEDIA_ROOT, str(doctor.image))
        image = Image(image_path, width=0.8 * inch, height=0.8 * inch)

        

        data.append([reordered_speciality, reordered_medical_education_number, reordered_last_name, reordered_first_name, image])
    table = Table(data, colWidths=[2.0 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'tahoma'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 1), (-1, -1), 'tahoma'),
    ('FONTSIZE', (0, 1), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, -1), (-1, -1), 'tahoma'),
    ('FONTSIZE', (0, -1), (-1, -1), 12),
    ('TOPPADDING', (0, -1), (-1, -1), 12),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, 300)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')




