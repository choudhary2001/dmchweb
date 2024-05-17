from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Min, Max
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
import pytz
from collections import Counter
import json
from django.forms.models import model_to_dict
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
# Get the current time in UTC
current_time_utc = timezone.now()

# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)


@login_required
def fetch_ipd_patient_data(request):
    if request.method == 'GET' and 'regid' in request.GET:
        regid = request.GET.get('regid')
        try:
            # patient = Patient.objects.filter(regid=regid).first()
            patient = Patient.objects.filter(Q(regid=regid) | Q(regnoid=regid)).first()

            data = {
                'patient' : model_to_dict(patient)
            }
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def ipd_departments(request):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':
        if request.method == "POST":
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            d = IpdDepartment(name = department, room_no = room_no)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = IpdDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : d,
            'title' : 'Departments'
        }
        return render(request, 'ipd/departments.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_update(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'IPD' :
        if request.method == "POST":
            d = IpdDepartment.objects.filter(department_id =department_id).first()
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            print(room_no)
            dc = IpdDepartment.objects.filter(name = department).first()
            if not dc or dc.name == department:
                d.name = department
                d.room_no = room_no
                d.save()
                messages.success(request, 'Department updated successfully.')
            else:
                messages.error(request, 'Department name already exists.')

        return redirect('ipd_departments')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_delete(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'IPD' :
        d = IpdDepartment.objects.filter(department_id =department_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('ipd_departments')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def ipd_doctors(request):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':
        if request.method == "POST":
            doctor = request.POST['doctor']
            department = request.POST['department']
            de = IpdDepartment.objects.filter(department_id =department).first()

            d = IpdDoctor(name = doctor, department = de)
            d.save()
            messages.success(request, 'Doctor added successfully.')
        d = IpdDoctor.objects.all().order_by('created_at')
        de = IpdDepartment.objects.all().order_by('created_at')

        context = {
            'doctors' : d,
            'departments' : de,
            'title' : "Doctors"
        }
        return render(request, 'ipd/doctors.html', context = context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors_update(request, doctor_id):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':
        if request.method == "POST":
            d = IpdDoctor.objects.filter(doctor_id =doctor_id).first()
            doctor = request.POST['doctor']
            department = request.POST['department']
            de = IpdDepartment.objects.filter(department_id =department).first()

            dc = IpdDoctor.objects.filter(name = doctor).all()
            # if not dc:
            d.name = doctor
            d.department = de
            d.save()
            messages.success(request, 'Doctor updated successfully.')
            # else:
            #     messages.error(request, 'Doctor name already exists.')
        return redirect('ipd_doctors')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors_delete(request, doctor_id):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':
        d = IpdDoctor.objects.filter(doctor_id =doctor_id).first()
        d.delete()
        messages.success(request, 'Doctor updated successfully.')

        return redirect('ipd_doctors')
    else:
        logout(request)
        return redirect('signin') 
    

@csrf_exempt
def get_ipd_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    print(department_id)
    d = IpdDepartment.objects.filter(department_id =department_id).first()
    doctors = IpdDoctor.objects.filter(department=d).values('doctor_id', 'name')
    return JsonResponse({'doctors': list(doctors)})

@login_required
def ipd_add_patient(request):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':

        if request.method == 'POST':
            try:
                regid = request.POST.get('regid')
                name = request.POST.get('name')
                guardiannametitle = request.POST.get('guardiannametitle')
                guardianname = request.POST.get('guardianname')
                year = request.POST.get('year', 0)
                month = request.POST.get('month', 0)
                days = request.POST.get('days', 0)
                gender = request.POST.get('gender')
                mobno = request.POST.get('mobile')
                address = request.POST.get('address')
                policest = request.POST.get('policest')
                district = request.POST.get('district')
                pincode = request.POST.get('pincode')
                doctor = request.POST.get('doctor')
                department = request.POST.get('department')
                disease = request.POST.get('disease')
                admit_date = request.POST.get('admit_date')

                if year.isdigit() :
                    year = int(year)
                else:
                    year = 0

                if month.isdigit():
                    month = int(month)
                else:
                    month = 0
                
                if days.isdigit():
                    days = int(days)
                else:
                    days = 0

                de = IpdDepartment.objects.filter(department_id = department).first()
                d = IpdDoctor.objects.filter(doctor_id = doctor).first()
                p = Patient.objects.filter(regid = regid).first()

                patient = Patient_Admission.objects.create(
                    user = request.user,
                    patient = p,
                    regno = regid,
                    name=name,
                    guardiannametitle=guardiannametitle,
                    guardianname=guardianname,
                    year=year,
                    month=month,
                    days=days,
                    gender=gender,
                    mobno=mobno,
                    address=address,
                    policest=policest,
                    district=district,
                    # state=state,
                    pincode=pincode,
                    disease=disease,
                    referby=d,
                    department=de,
                    appointment_date = admit_date
                )
                messages.success(request, 'Patient Admitted Successfully')
 
                # return render(request, 'counter/patientsprint.html', {"patient" : patient})
                return redirect('ipd_add_patient')

            except Exception as e:
                print(e)
                messages.error(request, 'Some error occured please fill correctly')
                return redirect('ipd_add_patient')
                
        de = IpdDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : de,
            'title' : "Patient Registration",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'ipd/add_investigation.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 

@login_required
def fetch_ipd_decharge_patient_data(request):
    if request.method == 'GET' and 'regid' in request.GET:
        regid = request.GET.get('regid')
        try:
            # patient = Patient.objects.filter(regid=regid).first()
            patient = Patient_Admission.objects.filter(regno=regid).first()
            print(patient.discharge)
            if patient.discharge == False:
                data = {
                    'patient' : model_to_dict(patient),
                    'department' : patient.department.name,
                    'doctor' : patient.referby.name,

                }
            else:
                data = {
                    'patient' : {}
                }
            print(data)
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)




@login_required
def update_ipd_patient(request, patient_dmission_id):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':
        pa = Patient_Admission.objects.filter(patient_dmission_id = patient_dmission_id).first()

        if request.method == "POST":

            regid = request.POST.get('regid')
            name = request.POST.get('name')
            guardiannametitle = request.POST.get('guardiannametitle')
            guardianname = request.POST.get('guardianname')
            year = request.POST.get('year', 0)
            month = request.POST.get('month', 0)
            days = request.POST.get('days', 0)
            gender = request.POST.get('gender')
            mobno = request.POST.get('mobile')
            address = request.POST.get('address')
            policest = request.POST.get('policest')
            district = request.POST.get('district')
            pincode = request.POST.get('pincode')
            doctor = request.POST.get('doctor')
            department = request.POST.get('department')
            disease = request.POST.get('disease')
            admit_date = request.POST.get('admit_date')
            discharge_date = request.POST.get('discharge_date')
            discharge = request.POST.get('discharge')
            death = request.POST.get('death')
            lama = request.POST.get('lama')

            if year.isdigit() :
                year = int(year)
            else:
                year = 0

            if month.isdigit():
                month = int(month)
            else:
                month = 0
            
            if days.isdigit():
                days = int(days)
            else:
                days = 0

            p = Patient.objects.filter(regid = regid).first()


            de = IpdDepartment.objects.filter(department_id = department).first()
            d = IpdDoctor.objects.filter(doctor_id = doctor).first()
            
            pa.patient = p
            pa.regno = regid
            pa.name=name
            pa.guardiannametitle=guardiannametitle
            pa.guardianname=guardianname
            pa.year=year
            pa.month=month
            pa.days=days
            pa.gender=gender
            pa.mobno=mobno
            pa.address=address
            pa.policest=policest
            pa.district=district
            pa.pincode=pincode
            pa.disease=disease
            pa.referby=d
            pa.department=de
            pa.appointment_date = admit_date
            pa.discharge_date = discharge_date
            pa.death = death
            pa.lama = lama
            
            # Save the updated patient object
            p.save()

            messages.success(request, 'Patient Updated Successfully')

            return redirect(f'/ipd/update-patient/{pa.patient_dmission_id}/')

        ide = IpdDepartment.objects.all().order_by('-created_at')
        
        context = {
            'patient' : pa,
            'departments' : ide,
            'title' : 'Update Patient Details'
        }
        print(context)
        return render(request, 'ipd/investigationedit.html', context= context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def delete_patients(request, pk):
    if request.user.is_superuser:
        p = Patient_Admission.objects.filter(regid = pk, de = None).first()
        if p is not None:
            p.delete()
        return redirect('show_patients')
    else:
        logout(request)
        return redirect('signin') 




@login_required
def ipd_discharge_patient(request):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':

        if request.method == 'POST':
            try:
                regid = request.POST.get('regid')
                death = request.POST.get('death')
                lama = request.POST.get('lama')
                discharge_date = request.POST.get('discharge_date')
                print(death, lama, discharge_date)

                p = Patient.objects.filter(regid = regid).first()
                pd = Patient_Admission.objects.filter(regno = regid).order_by('-appointment_date').first()
                pd.discharge_date = discharge_date
               
                pd.lama= lama
                pd.death = death
                pd.save()

                messages.success(request, 'Patient Discharged Successfully')
 
                # return render(request, 'counter/patientsprint.html', {"patient" : patient})
                return redirect('ipd_discharge_patient')

            except Exception as e:
                print(e)
                messages.error(request, 'Some error occured please fill correctly')
                return redirect('ipd_discharge_patient')
                
        de = IpdDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : de,
            'title' : "Patient Discharge",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'ipd/discharge_patient.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 

def show_ipd_patients_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'IPD':

        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department')

        # Convert the date strings to datetime objects
        if start_date_str:
            start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            # Adjust the end date to include all records for that day
            end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        

        patients = Patient_Admission.objects.all().order_by('-appointment_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            patients = patients.filter(appointment_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            patients = patients.filter(appointment_date__gte=start_date, appointment_date__lt=next_day)
        elif end_date:
            patients = patients.filter(appointment_date__lt=end_date)
        
        de = IpdDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : de,
            'title' : f"Total Patient Report : {len(patients)}",
            'patients' : patients
        }
        return render(request, 'ipd/patient_data.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 