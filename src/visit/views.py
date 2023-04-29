from django.shortcuts import render
from django.http import JsonResponse
from .models import Speciality, Doctor, WeeklySchedule, Appointment, Patient, TimeSlot
from django.views.decorators.csrf import csrf_exempt
def main_view(request):
    return render(request, 'pages/home.html', {})




def get_json_speciality_data(request):
    query_set = list(Speciality.objects.values())
    return JsonResponse({'data':query_set})


def get_json_doctor_data(request, *args, **kwargs):
    selected_speciality = kwargs.get('speciality_id')
    obj_models = list(Doctor.objects.filter(speciality_id = selected_speciality).values())
    return JsonResponse({'data':obj_models})




def get_json_schedule(request, *args, **kwargs):
    selected_doctor = kwargs.get('doctor_id')
    obj_models = list(
        WeeklySchedule.objects
        .filter(doctor__id=selected_doctor)
        .values('doctor', 'day_of_week', 'time_slots__start_time', 'time_slots__end_time')
    )
    return JsonResponse({'data': obj_models})





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid

@csrf_exempt
def create_appointment(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        doctor_id = request.POST.get('doctor')
        day = request.POST.get('day')
        patient_first_name = request.POST.get('patient[first_name]')
        patient_last_name = request.POST.get('patient[last_name]')
        patient_phone = request.POST.get('patient[phone]')
        time_slot_id = request.POST.get('time_slot')
        
        # Check if the time slot exists
        if not TimeSlot.objects.filter(id=time_slot_id).exists():
            return JsonResponse({'error': 'Invalid Time Slot ID'}, status=400)
        
        # Create a new appointment
        appointment = Appointment.objects.create(
            doctor_id=doctor_id,
            day=day,
            patient_first_name=patient_first_name,
            patient_last_name=patient_last_name,
            patient_phone=patient_phone,
            time_slot_id=time_slot_id
        )
        
        # Return the appointment tracking number as a JSON response
        response_data = {
            'tracking_number': appointment.tracking_number
        }
        return JsonResponse(response_data)
    
    # Return a 400 Bad Request error if the request is not valid
    return JsonResponse({'error': 'Invalid Request'}, status=400)
    