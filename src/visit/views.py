from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Speciality, Doctor, WeeklySchedule, Appointment, Patient, TimeSlot
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.db import transaction
import json



def main_view(request):
    return render(request, 'pages/home.html', {})




def get_json_schedule_data(request):
    query_set = WeeklySchedule.objects.values('doctor__first_name', 'doctor__last_name', 'day_of_week')
    data = list(query_set)
    return JsonResponse({'data': data})


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
    weekly_schedules = WeeklySchedule.objects.filter(doctor_id=selected_doctor)

    # Construct a list of dictionaries representing the weekly schedule
    schedule_list = []
    for schedule in weekly_schedules:
        time_slots = schedule.time_slots.all()
        time_slots_data = [
            {'start_time': slot.start_time.strftime('%H:%M'), 'end_time': slot.end_time.strftime('%H:%M')} for slot in time_slots
        ]
        schedule_data = {
            'doctor': schedule.doctor_id,
            'day_of_week': schedule.day_of_week,
            'time_slots': time_slots_data
        }
        schedule_list.append(schedule_data)

    # Check if each time slot is booked
    for schedule in schedule_list:
        for time_slot in schedule['time_slots']:
            is_booked = Appointment.objects.filter(
                doctor_id=schedule['doctor'],
                day=schedule['day_of_week'],
                time_slot__start_time=time_slot['start_time'],
                time_slot__end_time=time_slot['end_time']
            ).exists()
            time_slot['is_booked'] = is_booked

    # Convert the list of dictionaries to JSON
    json_data = json.dumps(schedule_list)

    return JsonResponse({'data': json_data}, safe=False)





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




