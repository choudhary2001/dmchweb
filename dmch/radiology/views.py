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
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
# Get the current time in UTC
current_time_utc = timezone.now()

# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)


@csrf_exempt
def get_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    print(department_id)
    d = RadiologyDepartment.objects.filter(department_id =department_id).first()
    doctors = RadiologyDoctor.objects.filter(department=d).values('doctor_id', 'name')
    return JsonResponse({'doctors': list(doctors)})

@csrf_exempt
def get_investigation_by_department(request):
    investigation_unit = request.GET.get('investigation_unit')
    print(investigation_unit)
    investigation = Investigation.objects.filter(investigation_unit=investigation_unit).values('investigation_id', 'name')
    units = SubUnit.objects.filter(sub_unit=investigation_unit).values('sub_unit_iid', 'name')
    return JsonResponse({'investigation': list(investigation), 'unit': list(units)})


@login_required
def departments(request):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            d = RadiologyDepartment(name = department, room_no = room_no)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = RadiologyDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : d,
            'title' : 'Departments'
        }
        return render(request, 'radiology/departments.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_update(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            d = RadiologyDepartment.objects.filter(department_id =department_id).first()
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            print(room_no)
            dc = RadiologyDepartment.objects.filter(name = department).first()
            if not dc or dc.name == department:
                d.name = department
                d.room_no = room_no
                d.save()
                messages.success(request, 'Department updated successfully.')
            else:
                messages.error(request, 'Department name already exists.')

        return redirect('radiology_departments')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_delete(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        d = RadiologyDepartment.objects.filter(department_id =department_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('radiology_departments')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors(request):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            doctor = request.POST['doctor']
            department = request.POST['department']
            de = RadiologyDepartment.objects.filter(department_id =department).first()

            d = RadiologyDoctor(name = doctor, department = de)
            d.save()
            messages.success(request, 'Doctor added successfully.')
        d = RadiologyDoctor.objects.all().order_by('created_at')
        de = RadiologyDepartment.objects.all().order_by('created_at')

        context = {
            'doctors' : d,
            'departments' : de,
            'title' : "Doctors"
        }
        return render(request, 'radiology/doctors.html', context = context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors_update(request, doctor_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            d = RadiologyDoctor.objects.filter(doctor_id =doctor_id).first()
            doctor = request.POST['doctor']
            department = request.POST['department']
            de = RadiologyDepartment.objects.filter(department_id =department).first()

            dc = RadiologyDoctor.objects.filter(name = doctor).all()
            # if not dc:
            d.name = doctor
            d.department = de
            d.save()
            messages.success(request, 'Doctor updated successfully.')
            # else:
            #     messages.error(request, 'Doctor name already exists.')
        return redirect('radiology_doctors')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors_delete(request, doctor_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        d = RadiologyDoctor.objects.filter(doctor_id =doctor_id).first()
        d.delete()
        messages.success(request, 'Doctor updated successfully.')

        return redirect('radiology_doctors')
    else:
        logout(request)
        return redirect('signin') 
    

@login_required
def investigations(request):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            name = request.POST['name']
            department_unit = request.POST['department_unit']
            d = Investigation(name = name, investigation_unit = department_unit)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = Investigation.objects.all().order_by('-created_at')
        context = {
            'investigations' : d,
            'title' : 'Investigations'
        }
        return render(request, 'radiology/investigations.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def investigationss_update(request, investigation_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            d = Investigation.objects.filter(investigation_id =investigation_id).first()
            name = request.POST['name']
            department_unit = request.POST['department_unit']
 
            d.name = name
            d.investigation_unit = department_unit
            d.save()
            messages.success(request, 'Department updated successfully.')

        return redirect('radiology_investigations')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def investigations_delete(request, investigation_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        d = Investigation.objects.filter(investigation_id =investigation_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('radiology_investigations')
    else:
        logout(request)
        return redirect('signin') 


@login_required
def radiology_sub_unit(request):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            name = request.POST['name']
            department_unit = request.POST['department_unit']
            d = SubUnit(name = name, sub_unit = department_unit)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = SubUnit.objects.all().order_by('-created_at')
        context = {
            'investigations' : d,
            'title' : 'Investigations'
        }
        return render(request, 'radiology/sub_unit.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def radiology_sub_unit_update(request, sub_unit_iid):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        if request.method == "POST":
            d = SubUnit.objects.filter(sub_unit_iid =sub_unit_iid).first()
            name = request.POST['name']
            department_unit = request.POST['department_unit']
 
            d.name = name
            d.sub_unit = department_unit
            d.save()
            messages.success(request, 'Department updated successfully.')

        return redirect('radiology_sub_unit')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def radiology_sub_unit_delete(request, sub_unit_iid):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        d = SubUnit.objects.filter(sub_unit_iid =sub_unit_iid).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('radiology_investigations')
    else:
        logout(request)
        return redirect('signin') 


@login_required
def add_radiology_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':

        # Get the current time in UTC
        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)
        print(current_time_kolkata)



        if request.method == 'POST':
            print(request.POST)
            regid = request.POST.get('regid')
            patient_name = request.POST.get('patient_name')
            department = request.POST.get('department')
            doctor = request.POST.get('doctor')
            investigation_ids = request.POST.getlist('investigation')
            department_unit = request.POST.get('department_unit')
            patient_type = request.POST.get('patient_type')
            investigation_type = request.POST.get('investigation_type')
            no_of_plate = request.POST.get('no_of_plate', None)
            plate_size = request.POST.getlist('plate_size')
            sub_unit = request.POST.get('sub_unit')
            date = request.POST.get('date')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            try:
                p = Patient.objects.filter(regid = regid).first()
            except Exception as e:
                print(e)
                try:
                    p = Patient.objects.filter(regnoid = regid).first()
                except Exception as e:
                    print(e)
                    p = None

            if p is None:
                try:
                    years, months, days = extract_duration(age)

                    p = Patient.objects.create(
                        user = request.user,
                        de = 'Radiology',
                        gender = gender,
                        year = years,
                        month = months,
                        days = days,
                    )
                except Exception as e:
                    print(e)
                    p = Patient.objects.create(
                        user = request.user,
                        de = 'Radiology',
                        gender = gender
                    )
                if regid:
                    p.regnoid = regid
                if patient_name:
                    p.name = patient_name
                p.save()
            print(p)
            
            de = RadiologyDepartment.objects.filter(department_id = department).first()
            d = RadiologyDoctor.objects.filter(doctor_id = doctor).first()
            # ie = Investigation.objects.filter(investigation_id = investigation).first()
            investigation = ''
            for i in investigation_ids:
                investigations = Investigation.objects.filter(investigation_id=i).first()
                investigation  += f"{investigations.name}, "
            print(investigation)
            patient = Radiology.objects.create(
                user = request.user,
                patient_name=patient_name,
                reg_no=regid,
                doctor=d,
                patient=p,
                department=de,
                investigation_unit=department_unit,
                patient_type=patient_type,
                investigation_type=investigation_type,
                no_of_plate=no_of_plate,
                plate_size=plate_size,
                sub_unit = sub_unit,
                add_time=date,
                investigations = investigation
            )


            request.session['radiology_date'] = date
            messages.success(request, 'Added Successfully.')


        des = RadiologyDepartment.objects.all().order_by('-created_at')
        ie = Investigation.objects.all().order_by('-created_at')
        context = {
            'departments' : des,
            'investigations' : ie,
            'title' : "Add Report",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'radiology/add_report.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 


@login_required
def show_radiology_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name')
        department_id = request.GET.get('department')
        doctor_id = request.GET.get('doctor')
        department_unit = request.GET.get('department_unit')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Radiology.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)
        elif end_date:
            r = r.filter(__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = RadiologyDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    r = r.filter(department = de)
                    print(r)
                    department = de.name

        investigation_unit = None
        if department_unit != None:
            if department_unit != 'All':
                r = r.filter(investigation_unit = department_unit)
                print(r)
                investigation_unit = department_unit

        doctor = None
        if doctor_id != None:
            if doctor_id != 'All':
                de = RadiologyDoctor.objects.filter(doctor_id = doctor_id).first()
                print(de)
                if de:
                    r = r.filter(doctor = de)
                    print(r)
                    doctor = de.name

        ie = Investigation.objects.all().order_by('-created_at')
        de = RadiologyDepartment.objects.all().order_by('name')
        do = RadiologyDoctor.objects.all().order_by('name')
        
        context = {
            'departments' : de,
            'doctors' : do,
            'investigations' : ie,
            'title' : f"Show Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'radiology' : r,
            'investigation_unit' : investigation_unit
        }
        return render(request, 'radiology/radiology.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 



@login_required
def print_radiology_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name')
        department_id = request.GET.get('department')
        department_unit = request.GET.get('department_unit')
        doctor_id = request.GET.get('doctor')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Radiology.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)
        elif end_date:
            r = r.filter(created_at__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = RadiologyDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    r = r.filter(department = de)
                    print(r)
                    department = de.name

        investigation_unit = None
        if department_unit != None:
            if department_unit != 'All':
                r = r.filter(investigation_unit = department_unit)
                print(r)
                investigation_unit = department_unit

        doctor = None
        if doctor_id != None:
            if doctor_id != 'All':
                de = RadiologyDoctor.objects.filter(doctor_id = doctor_id).first()
                print(de)
                if de:
                    r = r.filter(doctor = de)
                    print(r)
                    doctor = de.name

        ie = Investigation.objects.all().order_by('-created_at')
        de = RadiologyDepartment.objects.all().order_by('name')
        do = RadiologyDoctor.objects.all().order_by('name')
        
        context = {
            'departments' : de,
            'doctors' : do,
            'investigations' : ie,
            'title' : f"Show Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'radiology' : r,
            'investigation_unit' : investigation_unit,
            'start_date_str' : start_date_str,
            'end_date_str' : end_date_str
        }
        return render(request, 'radiology/radiology_print.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 

@login_required
def delete_radiology_report(request, radiology_id):
    if request.user.is_superuser or request.session['user_role'] == 'Radiology':
        r = Radiology.objects.filter(radiology_id = radiology_id).first()
        if r:
            r.delete()
        
        messages.success(request, 'Report deleted successfully.')

        return redirect('show_radiology_report')
    else:
        logout(request)
        return redirect('signin') 
