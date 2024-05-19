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

def home(request):
    return render(request, 'counter/home.html')

def signin(request):
    logout(request)
    request.session.clear()
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        p = Profile.objects.filter(user = user).first()
        print(p)
        if user is not None and user.is_active:
            # User is authenticated, log them in
            login(request, user)
            if user.is_superuser == False:
                d = DrugDepartment.objects.filter(name = p.user_role).first()
                sd = StoreDepartment.objects.filter(name = p.user_role).first()
                if p:
                    request.session['user_role'] = f"{p.user_role}"
                
                if p.user_role == 'Drug':
                    return redirect('/drug/product-type/add/')
                if p.user_role == 'Pathology':
                    return redirect('/pathology/create_test_report/')

                if p.user_role == 'Radiology':
                    return redirect('/radiology/add-report/')
                    
                if d is not None:
                    request.session['user_role_store'] = "Medicine Store"
                    return redirect('/medicine_store/supply/view/')
                if sd is not None:
                    request.session['user_role_store'] = "Store"
                    return redirect('/store/add-products/')
                return redirect('add_patient')
            # messages.success(request, "You have successfully signed in.")
            request.session['user_role'] = 'Admin'
            
            return redirect('departments')  # Redirect to dashboard or any other page
        else:
            # Authentication failed
            messages.error(request, "Invalid email or password. Please try again.")
    return render(request, 'counter/login.html')


@login_required
def fetch_patient_data_details(request):
    if request.method == 'GET' and 'regid' in request.GET:
        regid = request.GET.get('regid')
        try:
            # patient = Patient.objects.filter(regid=regid).first()
            try:
                regid_int = int(regid)
                # If no exception is raised, it means regid is an integer
                patient = Patient.objects.filter(Q(regid=regid_int) | Q(regnoid=regid)).first()
            except ValueError:
                # If regid cannot be converted to an integer, treat it as a varchar
                patient = Patient.objects.filter(regnoid=regid).first()
            print(patient.update_date)
            if patient is not None:
                thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
                # Check if the update_date is within the last 30 days
                if patient.appointment_date and patient.appointment_date >= thirty_days_ago:
                    available = True
                else:
                    available = False
                if patient.revisit == 'Revisit':
                    available = False
                print(available)
                report = {
                    'available' : available,
                    'id' : regid
                }


                data = {
                    'report' : report,
                }
            else:
                report = {
                    'available' : False,
                    'id' : None
                }
                data = {
                   'report' : report, 
                }
            print(data)

            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_patient(request):
    if request.user.is_superuser or request.session['user_role'] == 'Registration':

        # Get the current time in UTC
        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        print(current_time_kolkata)
        print(current_time_kolkata)

        p = Patient.objects.filter(de=None)
        pp = Patient.objects.filter(de=None).first()
        last_patient_pp = Patient.objects.filter(de=None).order_by('-appointment_date').first()
        if last_patient_pp:
            regid = int(last_patient_pp.regid) + 1
        else:
            regid = 1


        print(regid)
        # uhidno =int(latest_patient['uhidno__max']) + 1 if latest_patient['uhidno__max'] is not None else 1

        current_date = current_time_kolkata.date()
        uhidno = int(current_date.strftime('%y%m%d'))
        print(uhidno)

        start_date = current_date 
        end_date = current_date + timedelta(days=1) 

        latest_patient_today = Patient.objects.filter(appointment_date__gte=start_date, appointment_date__lt=end_date, de = None).order_by('-appointment_date').first()
        # latest_patient_today = Patient.objects.filter(appointment_date__lt=end_date).order_by('-appointment_date').first()
        if latest_patient_today:
            uhidnoincre = int(latest_patient_today.uhidnoincre) + 1
        else:
            uhidnoincre = 1

        if request.method == 'POST':
            try:
                paitient_type = request.GET.get('visit', None)
                if paitient_type:
                    paitient_type = 'Revisit'
                else:
                    paitient_type = None

                regid = request.POST.get('regid')
                # regnoid = request.POST.get('regnoid')
                # uhidno = request.POST.get('uhidno')
                # uhidnoincre = request.POST.get('uhidnoincre')
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
                visittype = request.POST.get('visittype')
                remarks = request.POST.get('remarks')
                redcard = request.POST.get('redcard', None)
                print(redcard)
                redcardtype = request.POST.get('redcardtype', None)
                print(redcard)
                redcardid = request.POST.get('redcardid', None)
                print(redcardid)

                if redcardtype == 'Red Card' or redcardtype == 'RB Case':
                    redcard = True
                else:
                    redcard = False

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

                # Check for duplicates
                try:
                    duplicate_patient = Patient.objects.filter(
                        name=name,
                        mobno=mobno,
                        guardianname=guardianname,
                        address = address,
                        de=None
                    ).exists()

                    if duplicate_patient:
                        messages.error(request, 'Duplicate patient found. Please check the details and try again.')
                        return redirect('add_patient')
                except Exception as e:
                    print(e)

                de = Department.objects.filter(department_id = department).first()
                d = Doctor.objects.filter(doctor_id = doctor).first()

                patient = Patient.objects.create(
                    user = request.user,
                    # regid=regid,
                    uhidno=uhidno,
                    uhidnoincre=uhidnoincre,
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
                    symptoms=remarks,
                    doctor=d,
                    department=de,
                    visittype=visittype,
                    redcard = redcard,
                    redcardid = redcardid,
                    redcardtype = redcardtype,
                    de = None
                )
                if paitient_type == 'Revisit':
                    rp = Patient.objects.filter(regid = regid).first()
                    rp.update_date = current_time_kolkata

                    patient.revisit = 'Revisit'
                    patient.revisitid = rp.regid
                    patient.symptoms = rp.symptoms
                    patient.doctor = rp.doctor
                    patient.department = rp.department
                    patient.visittype = rp.visittype
                    patient.save()

                    return render(request, 'counter/patientsprint.html', {"patient" : patient})
                return render(request, 'counter/patientsprint.html', {"patient" : patient})

            except Exception as e:
                print(e)
                messages.error(request, 'Some error occured please fill correctly')
                return redirect('add_patient')
                
        de = Department.objects.all().order_by('-created_at')
        context = {
            'patient' : p,
            'regid' : regid,
            'uhidno' : uhidno,
            'uhidnoincre' : uhidnoincre,
            'departments' : de,
            'title' : "Patient Registration",
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'counter/patientsadd.html', context=context) 
    else:
        logout(request)
        return redirect('signin') 


@csrf_exempt
def get_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    print(department_id)
    d = Department.objects.filter(department_id =department_id).first()
    doctors = Doctor.objects.filter(department=d).values('doctor_id', 'name')
    return JsonResponse({'doctors': list(doctors)})

@login_required
def show_patients(request):
    if request.user.is_superuser or request.session['user_role'] == 'Registration':

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
        
        # Filter patients based on the provided date range
        if request.user.is_superuser:
            patients = Patient.objects.filter(de=None).order_by('-appointment_date')
        else:
            patients = Patient.objects.filter(user = request.user, de = None).order_by('-appointment_date')


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
        
        
        non_price = 0
        red_card_total = 0
        rb_case_total = 0
        unkown_total = 0
        free_total = 0
        revisit_total = 0
        for p in patients:
            if p.visittype == 'Unknown':
                unkown_total += 1
            if p.visittype == 'Free':
                free_total += 1
            if p.redcard in [True, 'true']:  
                if p.redcardtype == 'Red Card':
                    red_card_total += 1
                if p.redcardtype == 'RB Case':
                    rb_case_total += 1
            if p.revisit == 'Revisit':
                revisit_total += 1


        non_price = red_card_total + rb_case_total + unkown_total + free_total + revisit_total
        # Count the total number of patients
        total = patients.count()

        total_amount = (int(total) * 5) - (non_price * 5)

        # Get visit type counts for filtered patients
        visittype_counts = patients.values('visittype').annotate(total_count=Count('visittype')).order_by()

        context = {
            'patients': patients,
            'title': f'Total Patients: {total}',
            'visittype_counts': visittype_counts,
            'total_amount' : total_amount,
            'current_time_kolkata' : current_time_kolkata,
            'redcard' : red_card_total,
            'rbcase': rb_case_total,
            'free_total' : free_total,
            'revisit_total' : revisit_total,
            'start_date_str' : start_date_str,
            'end_date_str' : end_date_str
        }
        print(context)
        return render(request, 'counter/patientsdata.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def show_patients_data(request):
    if request.user.is_superuser or request.session['user_role'] == 'Registration':
        # Your existing code here
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department = request.GET.get('department')
        # start_date = request.GET.get('start_date', None)
        # end_date = request.GET.get('end_date', None)

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

        # Filter patients based on the provided date range
        if request.user.is_superuser:
            # patients = Patient.objects.filter(de=None).order_by('-appointment_date')
            unique_departments = Profile.objects.exclude(main_department__isnull=True).values_list('main_department', flat=True).distinct()

            # Step 2: Find users that have those main_department values
            users_in_departments = User.objects.filter(profile__main_department__in=unique_departments)

            # Step 3: Find all Patient instances associated with those users
            patients = Patient.objects.filter(user__in=users_in_departments)
        else:
            patients = Patient.objects.filter(user = request.user, de = None).order_by('-appointment_date')

        search_query = request.GET.get('searchValue')



        url = search_query
        parsed_url = urlparse(url)
        query_string = parsed_url.query
        query_params = parse_qs(query_string)
        search_value_encoded = query_params.get('search', [''])[0]
        search_value_decoded = unquote_plus(search_value_encoded)

        print("Decoded search value:", search_value_decoded)

        # Filter patients based on search query
        if search_query:
            patients = patients.filter(
                Q(name__icontains=search_query) |
                Q(regid__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(doctor__name__icontains=search_query) |
                Q(department__name__icontains=search_query) |
                Q(visittype__icontains=search_query) |
                Q(revisit__icontains=search_query) |
                Q(redcardtype__icontains=search_query)
            )

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
        
        # Pagination
        page = request.GET.get('draw', 1)
        paginator = Paginator(patients, 10)  # Show 10 patients per page
        try:
            patients = paginator.page(page)
        except PageNotAnInteger:
            patients = paginator.page(1)
        except EmptyPage:
            patients = paginator.page(paginator.num_pages)
        print(patients)
        # Serialize patients data
        patients_data = []
        for patient in patients:
            if patient.doctor: 
                patient_doctor = patient.doctor.name 
            else: 
                patient_doctor = ''

            if patient.department: 
                patient_department = patient.department.name 
            else : 
                patient_department = ''

            if patient.redcardtype == 'Red Card': 
                patient_redcardtype = 'Red Card'
            else : 
                patient_redcardtype = ''

            if patient.revisit == 'Revisit': 
                patient_revisit = 'Re Visit'
            else : 
                patient_revisit = ''
            
            patients_data.append({
                'regid': patient.regid,
                'name': patient.name,
                'address': patient.address,
                'doctor': patient_doctor,
                'department': patient_department,
                'visittype': patient.visittype,
                'redcardtype': patient_redcardtype,
                'revisittype': patient_revisit,
                'appointment_date': patient.appointment_date,
            })

        p = Profile.objects.filter(user_role = 'Registration').all()
        registration_profiles = Profile.objects.filter(user_role='Registration')
    
        data = {
            'patients': patients_data,
            'has_next': patients.has_next(),
            'has_prev': patients.has_previous(),
            'draw': request.GET.get('draw'),  # Echo back the draw parameter
            'recordsTotal': paginator.count,  # Total records without filtering
            'recordsFiltered': paginator.count,  # Total records after filtering (for now)
            'data': patients_data
        }
        return JsonResponse(data)
    else:
        logout(request)
        return redirect('signin')



# @login_required
def show_patients_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Registration':

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')
        user_id = request.GET.get('user_id')
        location = request.GET.get('location')

        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%dT%H:%M')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%dT%H:%M')  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range
        if request.user.is_superuser:
            patients = Patient.objects.filter(de=None).order_by('-appointment_date')
            # unique_departments = Profile.objects.values_list('main_department', flat=True).distinct()
            unique_departments = Profile.objects.exclude(main_department__isnull=True).values_list('main_department', flat=True).distinct()

            # Step 2: Find users that have those main_department values
            users_in_departments = User.objects.filter(profile__main_department__in=unique_departments)

            # Step 3: Find all Patient instances associated with those users
            patients = Patient.objects.filter(user__in=users_in_departments)
        else:
            patients = Patient.objects.filter(user=request.user, de = None).order_by('-appointment_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            patients = patients.filter(appointment_date__range=(start_date, end_date), de = None)
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            patients = patients.filter(appointment_date__gte=start_datetime, appointment_date__lt=end_datetime, de = None)
        elif end_date:
            patients = patients.filter(appointment_date__lt=end_date, de = None)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = Department.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    patients = patients.filter(department = de, de = None)
                    print(patients)
                    department = de.name

        # users = None
        if user_id != None:
            if user_id != 'All':
                ue = User.objects.filter(id = user_id).first()
                print(ue)
                if ue:
                    patients = patients.filter(user = ue)
                    print(patients)
                    # department = de.name

        if location:
            if location != 'All':
                l_u_p = Profile.objects.filter(main_department=location).all()
            
                # Get the associated User instances
                l_u = User.objects.filter(profile__in=l_u_p)

                # Convert the queryset to a list of user IDs
                user_ids = l_u.values_list('id', flat=True)

                if user_ids:
                    patients = patients.filter(user_id__in=user_ids)
                    print(patients)

        # Count the total number of patients
        non_price = 0
        red_card_total = 0
        rb_case_total = 0
        unkown_total = 0
        free_total = 0
        revisit_total = 0
        for p in patients:
            if p.visittype == 'Unknown':
                unkown_total += 1
            if p.visittype == 'Free':
                free_total += 1
            if p.redcard in [True, 'true']:  
                if p.redcardtype == 'Red Card':
                    red_card_total += 1
                if p.redcardtype == 'RB Case':
                    rb_case_total += 1
            if p.revisit == 'Revisit':
                revisit_total += 1

        non_price = red_card_total + rb_case_total + unkown_total + free_total + revisit_total
        # Count the total number of patients
        total = patients.count()

        total_amount = (int(total) * 5) - (non_price * 5)

        # Get visit type counts for filtered patients
        visittype_counts = patients.values('visittype').annotate(total_count=Count('visittype')).order_by()

        date_range = start_date or end_date
        
        # Assuming `current_time_kolkata` is defined elsewhere in your code
        local_time = str(current_time_kolkata)
        d = Department.objects.all()
        min_appointment_date = patients.aggregate(Min('appointment_date'))['appointment_date__min']
        max_appointment_date = patients.aggregate(Max('appointment_date'))['appointment_date__max']
        show_patients = []
        print(min_appointment_date, max_appointment_date)
        if start_date_str or end_date_str or department_id:
            show_patients = patients

        p = Profile.objects.filter(user_role = 'Registration').all()
        registration_profiles = Profile.objects.filter(user_role='Registration')
        
        # Get the associated User instances
        registration_users = User.objects.filter(profile__in=registration_profiles)
    
        context = {
            'patients': show_patients,
            'title': f'Total Patients: {total}',
            'visittype_counts': visittype_counts,
            'current_time_kolkata': str(local_time),
            'redcard': red_card_total,
            'rbcase': rb_case_total,
            'departments' : d,
            'total_amount' : total_amount,
            'total_p' : total,
            'date_range' : date_range,
            'department' : department,
            'start_date' : min_appointment_date,
            'end_date' : max_appointment_date,
            'free_total' : free_total,
            'revisit_total' : revisit_total,
            'registration_users': registration_users,
        }
        return render(request, 'counter/Patientsreport.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def show_patients_report_userwise(request):
    if request.user.is_superuser:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department_id = request.GET.get('department')

        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range and user
        if request.user.is_superuser:
            users = User.objects.all()
            
        else:
            users = [request.user]

        total_patient = 0
        total_patient_amount = 0
        total_patient_count = 0
        total_patient_amount_count = 0

        users_with_patients = []
        if start_date_str or end_date_str:
            for user in users:
                pr = Profile.objects.filter(user = user).first()
                if pr:
                    if pr.user_role == 'Registration':
                        patients = Patient.objects.filter(user=user, de = None).order_by('-appointment_date')

                        if start_date and end_date:
                            patients = patients.filter(appointment_date__range=(start_date, end_date))
                        elif start_date:
                            next_day = start_date + timedelta(days=1)
                            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
                            end_datetime = start_datetime + timedelta(days=1)
                            patients = patients.filter(appointment_date__gte=start_datetime, appointment_date__lt=end_datetime)
                        elif end_date:
                            patients = patients.filter(appointment_date__lt=end_date)

                        department = None
                        if department_id and department_id != 'All':
                            department = Department.objects.filter(department_id=department_id).first()
                            if department:
                                patients = patients.filter(department=department)

                        # Calculate statistics
                        red_card_total = patients.filter(redcard=True, redcardtype='Red Card').count()
                        rb_case_total = patients.filter(redcard=True, redcardtype='RB Case').count()
                        unknown_total = patients.filter(visittype='Unknown').count()
                        free_total = patients.filter(visittype='Free').count()
                        revisit_total = patients.filter(revisit='Revisit').count()
                        total = patients.count()
                        non_price = red_card_total + rb_case_total + unknown_total + revisit_total
                        total_amount = (total * 5) - (non_price * 5)
                        total_patient =  total_patient + total
                        total_patient_count =  total_patient_count + total
                        total_patient_amount =  total_patient_amount + total_amount
                        total_patient_amount_count =  total_patient_amount_count + total_amount
                        # Get visit type counts
                        visittype_counts = patients.values('visittype').annotate(total_count=Count('visittype')).order_by()

                        min_appointment_date = patients.aggregate(Min('appointment_date'))['appointment_date__min']
                        max_appointment_date = patients.aggregate(Max('appointment_date'))['appointment_date__max']
                        p = Profile.objects.filter(user = user).first()
                        if p is not None:
                            if p.user_role == 'Registration':
                                if total_amount > 0:
                                    users_with_patients.append({
                                        'user': user,
                                        'patients': patients,
                                        'total': total,
                                        'redcard': red_card_total,
                                        'rbcase': rb_case_total,
                                        'unknown': unknown_total,
                                        'total_amount': total_amount,
                                        'visittype_counts': visittype_counts,
                                        'date_range': (start_date, end_date),
                                        'department': department,
                                        'start_date' : min_appointment_date,
                                        'end_date' : max_appointment_date,
                                        'free_total' : free_total,
                                        'revisit_total':revisit_total
                                    })
                
        d = Department.objects.all()
        context = {
            'users_with_patients': users_with_patients,
            'title': f'Patient Report',
            'departments' : d,
            'total_patient' : total_patient_count,
            'total_patient_amount' : total_patient_amount_count
        }
        return render(request, 'counter/Patientsreportuserwise.html', context = context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_patients(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Registration':

        paitient_type = request.GET.get('visit', None)
        if paitient_type:
            paitient_type = 'Revisit'
        else:
            paitient_type = None
        print(paitient_type)
        p = Patient.objects.filter(regid = pk, de = None).first()
        de = Department.objects.all().order_by('-created_at')
        if request.method == "POST":

            name = request.POST.get('name')
            guardiannametitle = request.POST.get('guardiannametitle')
            guardianname = request.POST.get('guardianname')
            year = int(request.POST.get('year', 0))
            month = int(request.POST.get('month', 0))
            days = int(request.POST.get('days', 0))
            gender = request.POST.get('gender')
            mobno = request.POST.get('mobile')
            address = request.POST.get('address')
            policest = request.POST.get('policest')
            district = request.POST.get('district')
            pincode = request.POST.get('pincode')
            doctor_id = request.POST.get('doctor')
            department_id = request.POST.get('department')
            visittype = request.POST.get('visittype')
            remarks = request.POST.get('remarks')

            de = Department.objects.filter(department_id = department_id).first()
            d = Doctor.objects.filter(doctor_id = doctor_id).first()
            
            # Update patient object with new values
            p.name = name
            p.guardiannametitle = guardiannametitle
            p.guardianname = guardianname
            p.year = year
            p.month = month
            p.days = days
            p.gender = gender
            p.mobno = mobno
            p.address = address
            p.policest = policest
            p.district = district
            p.pincode = pincode
            p.department = de
            p.doctor = d
            p.visittype = visittype
            p.symptoms = remarks
            
            # Save the updated patient object
            p.save()


            return redirect(f'/update-patients/{p.regid}')

        
        context = {
            'paitient_visit' : paitient_type,
            'patient' : p,
            'departments' : de,
            'title' : 'Update Patient Details',
            'current_time_kolkata' : current_time_kolkata,
        }
        print(context)
        return render(request, 'counter/patientsedit.html', context= context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def delete_patients(request, pk):
    if request.user.is_superuser:
        p = Patient.objects.filter(regid = pk, de = None).first()
        if p is not None:
            p.delete()
        return redirect('show_patients')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def dashboard(request):
    if request.user.is_superuser == False:
        return redirect('add_patient')
    # messages.success(request, "You have successfully signed in.")
    return redirect('departments')  # Redirect to dashboard or any other page
    # return render(request, 'counter/departments.html')

@login_required
def departments(request):
    if request.user.is_superuser:
        if request.method == "POST":
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            d = Department(name = department, room_no = room_no)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = Department.objects.all().order_by('-created_at')
        context = {
            'departments' : d,
            'title' : 'Departments'
        }
        return render(request, 'counter/departments.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_update(request, department_id):
    if request.user.is_superuser:
        if request.method == "POST":
            d = Department.objects.filter(department_id =department_id).first()
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            print(room_no)
            dc = Department.objects.filter(name = department).first()
            if not dc or dc.name == department:
                d.name = department
                d.room_no = room_no
                d.save()
                messages.success(request, 'Department updated successfully.')
            else:
                messages.error(request, 'Department name already exists.')

        return redirect('departments')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_delete(request, department_id):
    if request.user.is_superuser:
        d = Department.objects.filter(department_id =department_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('departments')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors(request):
    if request.user.is_superuser:
        if request.method == "POST":
            doctor = request.POST['doctor']
            department = request.POST['department']
            de = Department.objects.filter(department_id =department).first()

            d = Doctor(name = doctor, department = de)
            d.save()
            messages.success(request, 'Doctor added successfully.')
        d = Doctor.objects.all().order_by('created_at')
        de = Department.objects.all().order_by('created_at')

        context = {
            'doctors' : d,
            'departments' : de,
            'title' : "Doctors"
        }
        return render(request, 'counter/doctors.html', context = context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors_update(request, doctor_id):
    if request.user.is_superuser:
        if request.method == "POST":
            d = Doctor.objects.filter(doctor_id =doctor_id).first()
            doctor = request.POST['doctor']
            department = request.POST['department']
            de = Department.objects.filter(department_id =department).first()

            dc = Doctor.objects.filter(name = doctor).all()
            # if not dc:
            d.name = doctor
            d.department = de
            d.save()
            messages.success(request, 'Doctor updated successfully.')
            # else:
            #     messages.error(request, 'Doctor name already exists.')
        return redirect('doctors')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def doctors_delete(request, doctor_id):
    if request.user.is_superuser:
        d = Doctor.objects.filter(doctor_id =doctor_id).first()
        d.delete()
        messages.success(request, 'Doctor updated successfully.')

        return redirect('doctors')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def dataentryoperator(request):
    if request.user.is_superuser:
        if request.method == "POST":
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = request.POST['password']
            status = request.POST['status']
            user_role = request.POST['role']
            c_status = True
            if status == 'True':
                c_status = True
            else:
                c_status = False
            ue = User.objects.filter(username = email).first()
            hashed_password = make_password(password)
            if ue is None:
                u = User(first_name = first_name, last_name = last_name, username = email, email = email, password = hashed_password, is_active = c_status)
                u.save()
                p = Profile(user = u, user_role = user_role)
                p.save()
                messages.success(request, 'User added successfully.')
            else:
                messages.error(request, 'User already exists with this username.')
        d = Profile.objects.all().order_by('-created_at')
        de = DrugDepartment.objects.all().order_by('-created_at')
        sde = StoreDepartment.objects.all().order_by('-created_at')

        context = {
            'users' : d,
            'departments' : de,
            'sdepartments' : sde,
            'title' : 'Staff'
        }
        return render(request, 'counter/users.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def dataentryoperator_update(request, pk):
    if request.user.is_superuser:
        if request.method == "POST":
            d = User.objects.filter(id = pk).first()
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            password = request.POST['password']
            status = request.POST['status']
            user_role = request.POST['role']
            print(status)
            d.first_name = first_name
            d.last_name = last_name
            d.email = email
            p = Profile.objects.filter(user = d).first()
            if p:
                p.user_role = user_role
                p.save()
            else:
                pu = Profile(user = d, user_role = user_role)
                pu.save()
            if password:
                hashed_password = make_password(password)
                d.password = hashed_password
            c_status = True
            if status == 'True':
                c_status = True
            else:
                c_status = False
            d.is_active = c_status

            d.save()
            messages.success(request, 'User updated successfully.')

        return redirect('users')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def dataentryoperator_delete(request, pk):
    if request.user.is_superuser:
        d = User.objects.filter(id =pk).first()
        d.delete()
        messages.success(request, 'User deleted successfully.')

        return redirect('users')
    else:
        logout(request)
        return redirect('signin') 


def location_wise_report(request):
    if request.user.is_superuser:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')

        # Convert the date strings to datetime objects
        if start_date_str:
            start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')

        else:
            start_date = None

        if end_date_str:
            end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')  # Add one day to include end_date

        else:
            end_date = None
        

        # unique_departments = Profile.objects.filter(main_department).values_list('main_department', flat=True).distinct()
        unique_departments = Profile.objects.exclude(main_department__isnull=True).values_list('main_department', flat=True).distinct()
        # Step 2: Create a dictionary to store results
        department_data = []
        total_patient_count = 0
        total_patient_count_non_price = 0
        total_patient_amount_count = 0
        # Step 3: Iterate over each department and perform aggregations
        if start_date_str or end_date_str or department_id:
            for department in unique_departments:
                total_patient = 0
                total_patient_amount = 0
                users_in_department = User.objects.filter(profile__main_department=department)
                patients_in_department = Patient.objects.filter(user__in=users_in_department, de = None)
                
                if start_date and end_date:
                    patients_in_department = patients_in_department.filter(appointment_date__range=(start_date, end_date))
                elif start_date:
                    next_day = start_date + timedelta(days=1)
                    start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
                    end_datetime = start_datetime + timedelta(days=1)
                    patients_in_department = patients_in_department.filter(appointment_date__gte=start_datetime, appointment_date__lt=end_datetime)
                elif end_date:
                    patients_in_department = patients_in_department.filter(appointment_date__lt=end_date)

                # Calculate statistics
                red_card_total = patients_in_department.filter(redcard=True, redcardtype='Red Card').count()
                rb_case_total = patients_in_department.filter(redcard=True, redcardtype='RB Case').count()
                unknown_total = patients_in_department.filter(visittype='Unknown').count()
                free_total = patients_in_department.filter(visittype='Free').count()
                revisit_total = patients_in_department.filter(revisit='Revisit').count()
                total = patients_in_department.count()
                non_price = red_card_total + rb_case_total + unknown_total + revisit_total
                total_patient_count_non_price = total_patient_count_non_price + non_price
                total_amount = (total * 5) - (non_price * 5)
                total_patient_count =  total_patient_count + total
                total_patient_amount_count =  total_patient_amount_count + total_amount
                # Get visit type counts
                visittype_counts = patients_in_department.values('visittype').annotate(total_count=Count('visittype')).order_by()


                # Count total patients
                total_patients = patients_in_department.count()
                

                # Store the results in the dictionary
                department_data.append({
                    'main_department': department,
                    'total_patients': total,
                    'total_amount': total_amount,
                    'patients': list(patients_in_department.values('name', 'regno', 'uhidno', 'doctor__name', 'department__name', 'appointment_date'))
                })

        # Print or use the department_data as needed
        print(department_data)
        context = {
            'users_with_patients': department_data,
            'title': f'Patient Report',
            # # 'departments' : d,
            'total_patient' : total_patient_count,
            'total_patient_amount' : total_patient_amount_count,
            'total_patient_count_non_price' : total_patient_count_non_price,
            'start_date_str' : start_date_str,
            'end_date_str' : end_date_str
        }
        return render(request, 'counter/Patientsreportlocationwise.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    



@login_required
def department_wise_report(request):
    if request.user.is_superuser:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')

        # Convert the date strings to datetime objects
        if start_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')   # Add one day to include end_date
        else:
            end_date = None

        unique_departments = Profile.objects.exclude(main_department__isnull=True).values_list('main_department', flat=True).distinct()

        department_data = []
        total_patient_count = 0
        total_patient_count_non_price = 0
        total_patient_amount_count = 0



        if start_date or end_date or department_id:
            for department in unique_departments:
                total_patient = 0
                total_patient_amount = 0
                total_patient_count_date = 0
                total_patient_count_non_price_date = 0
                total_patient_amount_count_date = 0
                users_in_department = User.objects.filter(profile__main_department=department)
                patients_in_department = Patient.objects.filter(user__in=users_in_department, de=None)

                if start_date and end_date:
                    patients_in_department = patients_in_department.filter(appointment_date__range=(start_date, end_date))
                elif start_date:
                    start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
                    end_datetime = start_datetime + timedelta(days=1)
                    patients_in_department = patients_in_department.filter(appointment_date__gte=start_datetime, appointment_date__lt=end_datetime)
                elif end_date:
                    start_datetime = timezone.make_aware(end_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
                    end_datetime = start_datetime + timedelta(days=1)
                    patients_in_department = patients_in_department.filter(appointment_date__lt=end_date)

                # Calculate statistics
                red_card_total = patients_in_department.filter(redcard=True, redcardtype='Red Card').count()
                rb_case_total = patients_in_department.filter(redcard=True, redcardtype='RB Case').count()
                unknown_total = patients_in_department.filter(visittype='Unknown').count()
                free_total = patients_in_department.filter(visittype='Free').count()
                revisit_total = patients_in_department.filter(revisit='Revisit').count()
                total = patients_in_department.count()
                non_price = red_card_total + rb_case_total + unknown_total + revisit_total
                total_patient_count_non_price += non_price
                total_amount = (total * 5) - (non_price * 5)
                total_patient_count += total
                total_patient_amount_count += total_amount

                # Get visit type counts
                visittype_counts = patients_in_department.values('visittype').annotate(total_count=Count('visittype')).order_by()

                # Count total patients
                total_patients = patients_in_department.count()

                # Create date-wise data
                date_wise_data = []
                if start_date and end_date:
                    current_date = start_date
                    while current_date <= end_date:
                        total_patient_date = 0
                        total_patient_amount_date = 0
                        next_date = current_date + timedelta(days=1)
                        patients_on_date = patients_in_department.filter(appointment_date__date=current_date)
                                        # Calculate statistics
                        red_card_total_date = patients_on_date.filter(redcard=True, redcardtype='Red Card').count()
                        rb_case_total_date = patients_on_date.filter(redcard=True, redcardtype='RB Case').count()
                        unknown_total_date = patients_on_date.filter(visittype='Unknown').count()
                        free_total_date = patients_on_date.filter(visittype='Free').count()
                        revisit_total_date = patients_on_date.filter(revisit='Revisit').count()
                        total_date = patients_on_date.count()
                        non_price_date = red_card_total + rb_case_total_date + unknown_total_date + revisit_total_date
                        total_patient_count_non_price_date += non_price_date
                        total_amount_date = (total_date * 5) - (non_price_date * 5)
                        total_patient_count_date += total_date
                        total_patient_amount_count_date += total_amount_date

                        date_wise_data.append({
                            'date': current_date,
                            'total_patients': total_date,
                            'total_amount' : 5 * total_date,
                            'unpaid_patients' : non_price_date,
                            'total_paid' : total_amount_date

                        })
                        current_date = next_date

                # Store the results in the dictionary
                department_data.append({
                    'main_department': department,
                    'total_patients': total_patient_count_date,
                    'total_amount' : total_patient_count_date * 5,
                    'total_patient_count_non_price' : total_patient_count_non_price_date,
                    'total_patient_amount_count': total_patient_amount_count_date,
                    'date_wise_data': date_wise_data,
                })

        print(department_data)

        context = {
            'report_data': department_data,
            'title': 'Patient Report',
            'total_patient': total_patient_count,
            'total_patient_amount': total_patient_amount_count,
            'total_patient_count_non_price': total_patient_count_non_price,
            'start_date_str': start_date_str,
            'end_date_str': end_date_str
        }
        return render(request, 'counter/departmentreport.html', context=context)
    else:
        logout(request)
        return redirect('signin')



def signout(request):
    logout(request)
    request.session.clear()
    return redirect('signin') 