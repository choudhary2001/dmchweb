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
from radiology.models import *
# Get the current time in UTC
current_time_utc = timezone.now()

# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)



@login_required
def add_cardiology_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Crdiology':

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
            patient_type = request.POST.get('patient_type')
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
                        de = 'Crdiology',
                        gender = gender,
                        year = years,
                        month = months,
                        days = days,
                    )
                except Exception as e:
                    print(e)
                    p = Patient.objects.create(
                        user = request.user,
                        de = 'Crdiology',
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

            patient = Cardiology.objects.create(
                user = request.user,
                patient_name=patient_name,
                reg_no=regid,
                doctor=d,
                patient=p,
                department=de,
                patient_type=patient_type,
                add_time=date,
            )


            request.session['cardiology_date'] = date
            messages.success(request, 'Added Successfully.')


        des = RadiologyDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : des,
            'title' : "Add Report",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'cardiology/add_report.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 


@login_required
def show_cardiology_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Crdiology':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name')
        department_id = request.GET.get('department')
        doctor_id = request.GET.get('doctor')
        department_unit = request.GET.get('department_unit')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Cardiology.objects.all().order_by('-created_at')
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

      

        doctor = None
        if doctor_id != None:
            if doctor_id != 'All':
                de = RadiologyDoctor.objects.filter(doctor_id = doctor_id).first()
                print(de)
                if de:
                    r = r.filter(doctor = de)
                    print(r)
                    doctor = de.name

        de = RadiologyDepartment.objects.all().order_by('name')
        do = RadiologyDoctor.objects.all().order_by('name')
        
        context = {
            'departments' : de,
            'doctors' : do,
            'title' : f"Show Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'cardiology' : r,
        }
        return render(request, 'cardiology/cardiology.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 



@login_required
def print_cardiology_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Crdiology':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name')
        department_id = request.GET.get('department')
        department_unit = request.GET.get('department_unit')
        doctor_id = request.GET.get('doctor')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Cardiology.objects.all().order_by('-created_at')
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


        doctor = None
        if doctor_id != None:
            if doctor_id != 'All':
                de = RadiologyDoctor.objects.filter(doctor_id = doctor_id).first()
                print(de)
                if de:
                    r = r.filter(doctor = de)
                    print(r)
                    doctor = de.name

        de = RadiologyDepartment.objects.all().order_by('name')
        do = RadiologyDoctor.objects.all().order_by('name')
        
        context = {
            'departments' : de,
            'doctors' : do,
            'title' : f"Show Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'cardiology' : r,
            'start_date_str' : start_date_str,
            'end_date_str' : end_date_str
        }
        return render(request, 'cardiology/cardiology_print.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 

@login_required
def delete_cardiology_report(request, cardiology_id):
    if request.user.is_superuser or request.session['user_role'] == 'Crdiology':
        r = Cardiology.objects.filter(cardiology_id = cardiology_id).first()
        if r:
            r.delete()
        
        messages.success(request, 'Report deleted successfully.')

        return redirect('show_cardiology_report')
    else:
        logout(request)
        return redirect('signin') 
