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
from drug.models import *
from store.models import *
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlparse, parse_qs, unquote_plus

# Get the current time in UTC
current_time_utc = timezone.now()
from django.db.models import Q
# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)

from django.utils import timezone


def update_blood_stock_status():
    current_date = datetime.datetime.now().date()
    
    blood_stocks = BloodStock.objects.all()
    for stock in blood_stocks:
        if stock.add_date:
            add_date = stock.add_date.date()
            delta_days = (current_date - add_date).days
            
            if stock.blood_type == 'W/B' and delta_days > 30:
                stock.status = 'Expire'
            elif stock.blood_type == 'PRBC' and delta_days > 35:
                stock.status = 'Expire'
            elif stock.blood_type == 'FFP' and delta_days > 365:
                stock.status = 'Expire'
            elif stock.blood_type == 'PLT' and delta_days > 7:
                stock.status = 'Expire'
            
            stock.save()

@login_required
def issue_blood_add(request):
    if request.user.is_superuser or request.session['user_role'] == 'Blood Bank':
        update_blood_stock_status()
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
            patient_name = request.POST.get('patient_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            guardian_name = request.POST.get('guardian_name')
            address = request.POST.get('address')
            district = request.POST.get('district')
            mob_no = request.POST.get('mob_no')
            bag_no = request.POST.get('bag_no')
            blood_group = request.POST.get('blood_group')
            blood_type = request.POST.get('types')
            organization = request.POST.get('organization')
            organization_name = request.POST.get('organization_name')
            issue_type = request.POST.get('issue_type')
            issue_number = request.POST.get('card_no')
            issue_date = request.POST.get('issue_date')

            bsf = BloodStock.objects.filter(bag_no = bag_no, blood_group = blood_group, blood_type = blood_type ).order_by('add_date').first()
            if bsf:

                bi = BloodIssue.objects.create(
                    user = request.user,
                    patient_name = patient_name,
                    father_name = guardian_name,
                    gender = gender,
                    age = age,
                    address = address,
                    district = district,
                    mob_no = mob_no,
                    issue_bag_no = bag_no,
                    blood_group = blood_group,
                    blood_type = blood_type,
                    org_type = organization,
                    org_name = organization_name,
                    issue_type = issue_type,
                    issue_number = issue_number,
                    issue_date = issue_date
                )

                bsf.status = 'Donate'
                bsf.save()
                messages.success(request, 'Blood Issued Successfully.')

                return redirect(f"/blood-bank/issue-blood/")
            
        context = {
            'title' : 'Issue Blood',
            'current_time_kolkata' : current_time_kolkata

        }
        return render(request, 'blood_bank/issue_add.html', context = context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def issue_blood_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Blood Bank':
        update_blood_stock_status()
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        # Get the current time in UTC
        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)

        bi = BloodIssue.objects.all().order_by('-issue_date')

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
        if start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            bi = bi.filter(issue_date__gte=start_date, issue_date__lt=next_day)
        elif end_date:
            bi = bi.filter(issue_date__lt=end_date)

        elif start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            bi = bi.filter(issue_date__range=(start_date, end_date))
        
        context = {
            'title' : 'Issue Blood Report',
            'current_time_kolkata' : current_time_kolkata,
            'blood' : bi

        }
        return render(request, 'blood_bank/issue_data.html', context = context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def donate_blood_add(request):
    if request.user.is_superuser or request.session['user_role'] == 'Blood Bank':
        # Get the current time in UTC
        update_blood_stock_status()

        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)
        print(current_time_kolkata)
        if request.method == 'POST':
            patient_name = request.POST.get('patient_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            guardian_name = request.POST.get('guardian_name')
            address = request.POST.get('address')
            district = request.POST.get('district')
            mob_no = request.POST.get('mob_no')
            bag_no = request.POST.get('bag_no')
            blood_group = request.POST.get('blood_group')
            bag_type = request.POST.get('types')
            vd = request.POST.get('vd')
            vd_camp_name = request.POST.get('vd_camp_name')
            segment_no = request.POST.get('segment_no')
            add_date = request.POST.get('add_date')

            bi = BloodDonate.objects.create(
                user = request.user,
                donor_name = patient_name,
                father_name = guardian_name,
                gender = gender,
                age = age,
                address = address,
                district = district,
                mob_no = mob_no,
                vd = vd,
                vd_camp_name = vd_camp_name,
                segment_no = segment_no,
                bag_no = bag_no,
                blood_group = blood_group,
                bag_type = bag_type,
                add_date = add_date
            )

            if bag_type == 'Single':
                bs = BloodStock.objects.create(user = request.user, blooddonate = bi, segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'W/B', status = 'Active', add_date = add_date )
                bs.save()
            if bag_type == 'Tripple':
                bs1 = BloodStock.objects.create(user = request.user, blooddonate = bi, segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'PRBC', status = 'Active', add_date = add_date )
                bs1.save()
                bs2 = BloodStock.objects.create(user = request.user, blooddonate = bi, segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'FFP', status = 'Active', add_date = add_date )
                bs3 = BloodStock.objects.create(user = request.user, blooddonate = bi, segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'PLT', status = 'Active', add_date = add_date )


            messages.success(request, 'Blood Donated Successfully.')
            return redirect(f"/blood-bank/donate-blood/")
            
        context = {
            'title' : 'Donate Blood',
            'current_time_kolkata' : current_time_kolkata

        }
        return render(request, 'blood_bank/donate_add.html', context = context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def donate_blood_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Blood Bank':
        update_blood_stock_status()
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        # Get the current time in UTC
        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)
        print(current_time_kolkata)

        bi = BloodDonate.objects.all().order_by('-add_date')

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
        if start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            bi = bi.filter(add_date__gte=start_date, add_date__lt=next_day)
        elif end_date:
            bi = bi.filter(add_date__lt=end_date)

        elif start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            bi = bi.filter(add_date__range=(start_date, end_date))
        
        context = {
            'title' : 'Donate Blood Report',
            'current_time_kolkata' : current_time_kolkata,
            'blood' : bi

        }
        return render(request, 'blood_bank/donate_data.html', context = context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def blood_fetch_data(request):
    if request.user.is_superuser or request.user.is_staff or request.session['user_role'] == 'Blood Bank':
        update_blood_stock_status()

        if request.method == 'GET' and 'bag_no' in request.GET:
            bag_no = request.GET.get('bag_no')
            try:

                bs = BloodStock.objects.filter(bag_no = bag_no).order_by('add_date').first()

                if bs is not None:

                    data = {
                        'blood_group' : bs.blood_group,
                    }
                else:
                    data = {
                        'blood_group' : None
                    }
   
                print(data)

                return JsonResponse(data)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def blood_stocks(request):
    if request.user.is_superuser or  request.user.is_staff or request.session.get('user_role') == 'Blood Bank':
        if request.method == 'POST':
            stock_id = request.POST.get('stock_id')
            new_status = request.POST.get('new_status')
            blood_type = request.POST.get('blood_type')
            stock = BloodStock.objects.filter(id=stock_id, blood_type=blood_type).first()
            if stock:
                stock.status = new_status
                stock.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        blood_group = request.GET.get('blood_group', None)
        types = request.GET.get('types', None)
        bag_type = request.GET.get('bag_type', None)
        status = request.GET.get('status', None)
        bs = BloodStock.objects.all()

        current_time_utc = timezone.now()

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)

        if start_date_str:
            start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        else:
            end_date = None

        if start_date and end_date:
            bs = bs.filter(add_date__range=(start_date, end_date))
        elif start_date:
            bs = bs.filter(add_date__gte=start_date)
        elif end_date:
            bs = bs.filter(add_date__lt=end_date)

        print(blood_group, types, bag_type, status)

        if blood_group != None:
            if blood_group != 'All':
                bs = bs.filter(blood_group = blood_group)
        
        print(bs)

        if types != None:
            if types != 'All':
                bs = bs.filter(blood_type =types)

        print(bs)
        

        if bag_type != None:
            if bag_type != 'All':
                bs = bs.filter(bag_type =bag_type)

        print(bs)
        

        if status != None:
            if status != 'All':
                bs = bs.filter(status =status)

        print(bs)

        context = {
            'stock': bs,
            'start_date_str': start_date_str,
            'end_date_str': end_date_str,
            'blood_group' : blood_group,
            'types' : types,
            'bag_type' : bag_type,
            'status' : status,
            'title': f'Blood Stock, Total Stock: {bs.count()}'
        }
        return render(request, 'blood_bank/blood_stocks.html', context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def add_opening_stock(request):
    if request.user.is_superuser or request.session['user_role'] == 'Blood Bank':
        # Get the current time in UTC
        update_blood_stock_status()

        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)
        print(current_time_kolkata)
        if request.method == 'POST':

            bag_no = request.POST.get('bag_no')
            blood_group = request.POST.get('blood_group')
            bag_type = request.POST.get('types')
            segment_no = request.POST.get('segment_no')
            add_date = request.POST.get('add_date')


            if bag_type == 'Single':
                bs = BloodStock.objects.create(user = request.user, segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'W/B', status = 'Active', add_date = add_date )
                bs.save()
            if bag_type == 'Tripple':
                bs1 = BloodStock.objects.create(user = request.user, segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'PRBC', status = 'Active', add_date = add_date )
                bs1.save()
                bs2 = BloodStock.objects.create(user = request.user,  segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'FFP', status = 'Active', add_date = add_date )
                bs3 = BloodStock.objects.create(user = request.user,  segment_no = segment_no, bag_no = bag_no, blood_group = blood_group, bag_type = bag_type, blood_type = 'PLT', status = 'Active', add_date = add_date )


            messages.success(request, 'Added Successfully.')
            return redirect(f'/blood-bank/add-opening-stock/')
            
        context = {
            'title' : 'Opening Stock',
            'current_time_kolkata' : current_time_kolkata

        }
        return render(request, 'blood_bank/add_opening.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
