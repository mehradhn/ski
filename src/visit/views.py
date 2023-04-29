from django.shortcuts import render
from django.http import JsonResponse
from .models import Speciality, Doctor, WeeklySchedule, Appointment, Patient, TimeSlot
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.db import transaction
def main_view(request):
    return render(request, 'pages/home.html', {})




def get_json_speciality_data(request):
    query_set = list(Speciality.objects.values())
    return JsonResponse({'data':query_set})


def get_json_doctor_data(request, *args, **kwargs):
    selected_speciality = kwargs.get('speciality_id')
    obj_models = list(Doctor.objects.filter(speciality_id = selected_speciality).values())
    return JsonResponse({'data':obj_models})


def get_json_time_slot_data(request):
    query_sets = list(TimeSlot.objects.values())
    return JsonResponse({'data':query_sets})
    



def get_json_schedule(request, *args, **kwargs):
    selected_doctor = kwargs.get('doctor_id')
    obj_models = list(
        WeeklySchedule.objects
        .filter(doctor__id=selected_doctor)
        .values('doctor', 'day_of_week', 'time_slots__start_time', 'time_slots__end_time')
    )
    return JsonResponse({'data': obj_models})





@csrf_exempt
def create_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        day = request.POST.get('day')
        time_slot_id = request.POST.get('time_slot')
        first_name = request.POST.get('patient[first_name]')
        last_name = request.POST.get('patient[last_name]')
        phone_number = request.POST.get('patient[phone_number]')

        # Perform any additional validation or processing here

        with transaction.atomic():
            # Create the patient object
            patient = Patient.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )

            # Create the appointment object and associate it with the patient
            appointment = Appointment.objects.create(
                doctor_id=doctor_id,
                day=day,
                time_slot_id=time_slot_id,
                patient=patient
            )

            # Generate a tracking number
            tracking_number = appointment.generate_tracking_number()

        # Return a JSON response with the tracking number
        return JsonResponse({'data': {'tracking_number': tracking_number}})

    # Return an error response for invalid request methods
    return JsonResponse({'error': 'Invalid request method'})