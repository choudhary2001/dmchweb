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



@login_required
def add_bht_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Record Room':

        # Get the current time in UTC
        current_time_utc = timezone.now()

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)

        if request.method == 'POST':
            print(request.POST)
            patient_id = request.POST.get('patient_id')
            patient_name = request.POST.get('patient_name')
            department = request.POST.get('department')
            document = request.FILES.get('document')
            month = request.POST.get('month')
            year = request.POST.get('year')
            reason = request.POST.get('reason')
            icd = request.POST.get('icd')

            
            patient = BHT.objects.create(
                user = request.user,
                patient_id=patient_id,
                patient_name=patient_name,
                department = department,
                document = document,
                month=month,
                year=year,
                reason=reason,
                icd=icd,
            )

            messages.success(request, 'Added Successfully.')
            return redirect('/record-room/add-bht/')
        context = {
            'title' : "Add B.H.T",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'record_room/add_bht.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 


@login_required
def show_bht_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Record Room':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department', None)
        month = request.GET.get('month')
        year = request.GET.get('year')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = BHT.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)

        if department is not None:
            if department != 'All':
                r = r.filter(department=department)
        if month:
            if month != 'All':
                r = r.filter(month=month)
        if year:
            r = r.filter(year=year)

        unique_departments = BHT.objects.values_list('department', flat=True).distinct()
    
        context = {
            'title' : f"Show B.H.T Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'report' : r,
            'unique_departments' : unique_departments
        }
        return render(request, 'record_room/bht.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 



@login_required
def print_bht_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Record Room':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department', None)
        month = request.GET.get('month')
        year = request.GET.get('year')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = BHT.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)

        if department is not None:
            if department != 'All':
                r = r.filter(department=department)
        if month:
            if month != 'All':
                r = r.filter(month=month)
        if year:
            r = r.filter(year=year)

        unique_departments = BHT.objects.values_list('department', flat=True).distinct()
    
        context = {
            'title' : f"Show B.H.T Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'report' : r,
            'unique_departments' : unique_departments
        }
        return render(request, 'record_room/bht_print.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 



@login_required
def add_injuiry_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Record Room':

        # Get the current time in UTC
        current_time_utc = timezone.now()

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)

        if request.method == 'POST':
            print(request.POST)
            patient_id = request.POST.get('patient_id')
            patient_name = request.POST.get('patient_name')
            department = request.POST.get('department')
            document = request.FILES.get('document')
            month = request.POST.get('month')
            year = request.POST.get('year')
            reason = request.POST.get('reason')
            icd = request.POST.get('icd')

            
            patient = Injuiry.objects.create(
                user = request.user,
                patient_id=patient_id,
                patient_name=patient_name,
                department = department,
                document = document,
                month=month,
                year=year,
                reason=reason,
                icd=icd,
            )

            messages.success(request, 'Added Successfully.')
            return redirect('/record-room/add-injuiry/')
        context = {
            'title' : "Add Injuiry Report",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'record_room/add_injuiry.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 


@login_required
def show_injuiry_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Record Room':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department', None)
        month = request.GET.get('month')
        year = request.GET.get('year')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Injuiry.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)

        if department is not None:
            if department != 'All':
                r = r.filter(department=department)
        if month:
            if month != 'All':
                r = r.filter(month=month)
        if year:
            r = r.filter(year=year)

        unique_departments = Injuiry.objects.values_list('department', flat=True).distinct()
    
        context = {
            'title' : f"Show Injuiry Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'report' : r,
            'unique_departments' : unique_departments
        }
        return render(request, 'record_room/injuiry.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 

@login_required
def print_injuiry_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Record Room':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department', None)
        month = request.GET.get('month')
        year = request.GET.get('year')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Injuiry.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)

        if department is not None:
            if department != 'All':
                r = r.filter(department=department)
        if month:
            if month != 'All':
                r = r.filter(month=month)
        if year:
            r = r.filter(year=year)

        unique_departments = Injuiry.objects.values_list('department', flat=True).distinct()
    
        context = {
            'title' : f"Show Injuiry Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'report' : r,
            'unique_departments' : unique_departments
        }
        return render(request, 'record_room/injuiry_print.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 



@login_required
def add_death_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Record Room':

        # Get the current time in UTC
        current_time_utc = timezone.now()

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)

        if request.method == 'POST':
            print(request.POST)
            patient_id = request.POST.get('patient_id')
            patient_name = request.POST.get('patient_name')
            department = request.POST.get('department')
            document = request.FILES.get('document')
            month = request.POST.get('month')
            year = request.POST.get('year')
            reason = request.POST.get('reason')
            icd = request.POST.get('icd')

            
            patient = Death.objects.create(
                user = request.user,
                patient_id=patient_id,
                patient_name=patient_name,
                department = department,
                document = document,
                month=month,
                year=year,
                reason=reason,
                icd=icd,
            )

            messages.success(request, 'Added Successfully.')
            return redirect('/record-room/add-death/')
        context = {
            'title' : "Add Death Report",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'record_room/add_death.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 

@login_required
def show_death_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Record Room':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department', None)
        month = request.GET.get('month')
        year = request.GET.get('year')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Death.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)

        if department is not None:
            if department != 'All':
                r = r.filter(department=department)
        if month:
            if month != 'All':
                r = r.filter(month=month)
        if year:
            r = r.filter(year=year)

        unique_departments = Death.objects.values_list('department', flat=True).distinct()
    
        context = {
            'title' : f"Show Death Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'report' : r,
            'unique_departments' : unique_departments
        }
        return render(request, 'record_room/death.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 

@login_required
def print_death_report(request):

    if request.user.is_superuser or request.session['user_role'] == 'Record Room':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department = request.GET.get('department', None)
        month = request.GET.get('month')
        year = request.GET.get('year')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        r = Death.objects.all().order_by('-created_at')
        if start_date and end_date:
            r = r.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            r = r.filter(created_at__gte=start_date, created_at__lt=end_datetime)
            print(r)

        if department is not None:
            if department != 'All':
                r = r.filter(department=department)
        if month:
            if month != 'All':
                r = r.filter(month=month)
        if year:
            r = r.filter(year=year)

        unique_departments = Death.objects.values_list('department', flat=True).distinct()
    
        context = {
            'title' : f"Show Death Report : {len(r)}",
            'current_time_kolkata' : current_time_kolkata,
            'report' : r,
            'unique_departments' : unique_departments
        }
        return render(request, 'record_room/death_print.html', context=context)       
    else:
        logout(request)
        return redirect('signin') 

