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

# Get the current time in UTC
current_time_utc = timezone.now()

# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)

from django.utils import timezone



def signin(request):
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
                if p:
                    request.session['user_role'] = f"{p.user_role}"
                
                if p.user_role == 'Drug':
                    return redirect('/drug/product-type/add/')
                if p.user_role == 'Pathology':
                    return redirect('/pathology/create_test_report/')
                return redirect('add_patient')
            # messages.success(request, "You have successfully signed in.")
            request.session['user_role'] = 'Admin'
            
            return redirect('departments')  # Redirect to dashboard or any other page
        else:
            # Authentication failed
            messages.error(request, "Invalid email or password. Please try again.")
    return render(request, 'counter/login.html')


@login_required
def add_patient(request):
    # Get the current time in UTC
    current_time_utc = timezone.now()
    # request.session['user_role'] = 'Registration'

    # Get the Kolkata timezone
    kolkata_timezone = pytz.timezone('Asia/Kolkata')

    # Convert the current time to Kolkata timezone
    current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
    print(current_time_kolkata)
    print(current_time_kolkata)

    p = Patient.objects.all()
    pp = Patient.objects.all().first()
    last_patient_pp = Patient.objects.order_by('-appointment_date').first()
    if last_patient_pp:
        regno = int(last_patient_pp.regno) + 1
    else:
        regno = 1


    print(regno)
    # uhidno =int(latest_patient['uhidno__max']) + 1 if latest_patient['uhidno__max'] is not None else 1

    current_date = current_time_kolkata.date()
    uhidno = int(current_date.strftime('%y%m%d'))
    print(uhidno)

    start_date = current_date 
    end_date = current_date + timedelta(days=1) 
    # Check if the latest entry is from today or not
    # latest_patient = Patient.objects.filter(appointment_date__lt=end_date).aggregate(
    #     Max('uhidnoincre')
    # )

    # print(latest_patient)
    # next_day = start_date + timedelta(days=1)
    latest_patient_today = Patient.objects.filter(appointment_date__gte=start_date, appointment_date__lt=end_date).order_by('-appointment_date').first()
    # latest_patient_today = Patient.objects.filter(appointment_date__lt=end_date).order_by('-appointment_date').first()
    if latest_patient_today:
        uhidnoincre = int(latest_patient_today.uhidnoincre) + 1
    else:
        uhidnoincre = 1


    # If there are no entries for today, set the values to start from 1
    # if not all(latest_patient.values()):
    #     uhidnoincre = 1
    # else:
    #     uhidnoincre = int(latest_patient['uhidnoincre__max']) + 1 if latest_patient['uhidnoincre__max'] is not None else 1
    # print(uhidnoincre)

    if request.method == 'POST':
        try:
            # regno = request.POST.get('regno')
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

            de = Department.objects.filter(department_id = department).first()
            d = Doctor.objects.filter(doctor_id = doctor).first()

            while Patient.objects.filter(regno=regno).exists():
                regno += 1
    
            while Patient.objects.filter(appointment_date__gte=start_date, appointment_date__lt=end_date, uhidnoincre=uhidnoincre).exists():
                uhidnoincre += 1
    
            patient = Patient.objects.create(
                user = request.user,
                # regno=regno,
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
                redcardtype = redcardtype
            )
            return render(request, 'counter/patientsprint.html', {"patient" : patient})

        except Exception as e:
            print(e)
            messages.error(request, 'Some error occured please fill correctly')

    de = Department.objects.all().order_by('-created_at')
    context = {
        'patient' : p,
        'regno' : regno,
        'uhidno' : uhidno,
        'uhidnoincre' : uhidnoincre,
        'departments' : de,
        'title' : "Patient Registration",
        'current_time_kolkata' : current_time_kolkata
    }
    return render(request, 'counter/patientsadd.html', context=context) 

@csrf_exempt
def get_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    print(department_id)
    d = Department.objects.filter(department_id =department_id).first()
    doctors = Doctor.objects.filter(department=d).values('doctor_id', 'name')
    return JsonResponse({'doctors': list(doctors)})

@login_required
def show_patients(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
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
        patients = Patient.objects.all().order_by('-appointment_date')
    else:
        patients = Patient.objects.filter(user = request.user).order_by('-appointment_date')


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


    non_price = red_card_total + rb_case_total + unkown_total + free_total
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
        'free_total' : free_total
    }
    return render(request, 'counter/patientsdata.html', context=context)


# @login_required
def show_patients_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    department_id = request.GET.get('department')

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
        patients = Patient.objects.all().order_by('-appointment_date')
    else:
        patients = Patient.objects.filter(user=request.user).order_by('-appointment_date')

    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        patients = patients.filter(appointment_date__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
        end_datetime = start_datetime + timedelta(days=1)

        patients = patients.filter(appointment_date__gte=start_datetime, appointment_date__lt=end_datetime)
    elif end_date:
        patients = patients.filter(appointment_date__lt=end_date)

    department = None
    if department_id != None:
        if department_id != 'All':
            de = Department.objects.filter(department_id = department_id).first()
            print(de)
            if de:
                patients = patients.filter(department = de)
                print(patients)
                department = de.name

    # Count the total number of patients
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    free_total = 0
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

    non_price = red_card_total + rb_case_total + unkown_total + free_total
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
        'free_total' : free_total
    }
    return render(request, 'counter/Patientsreport.html', context=context)



@login_required
def show_patients_report_userwise(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    department_id = request.GET.get('department')

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
    
    # Filter patients based on the provided date range and user
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = [request.user]

    total_patient = 0
    total_patient_amount = 0

    users_with_patients = []
    for user in users:
        patients = Patient.objects.filter(user=user).order_by('-appointment_date')

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
        total = patients.count()
        non_price = red_card_total + rb_case_total + unknown_total
        total_amount = (total * 5) - (non_price * 5)
        total_patient =  total_patient + total
        total_patient_amount =  total_patient_amount + total_amount
        # Get visit type counts
        visittype_counts = patients.values('visittype').annotate(total_count=Count('visittype')).order_by()

        min_appointment_date = patients.aggregate(Min('appointment_date'))['appointment_date__min']
        max_appointment_date = patients.aggregate(Max('appointment_date'))['appointment_date__max']
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
                'free_total' : free_total
            })
    d = Department.objects.all()
    context = {
        'users_with_patients': users_with_patients,
        'title': f'Patient Report',
        'departments' : d,
        'total_patient' : total_patient,
        'total_patient_amount' : total_patient_amount
    }
    return render(request, 'counter/Patientsreportuserwise.html', context = context)



@login_required
def update_patients(request, pk):
    p = Patient.objects.filter(regno = pk).first()
    de = Department.objects.all().order_by('-created_at')
    if request.method == "POST":
        # if request.user.is_superuser:
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


        return redirect(f'/update-patients/{p.regno}')
        # else:
        #     logout(request)
        #     return redirect('signin') 
    context = {
        'patient' : p,
        'departments' : de,
        'title' : 'Update Patient Details',
        'current_time_kolkata' : current_time_kolkata
    }
    return render(request, 'counter/patientsedit.html', context= context)


@login_required
def delete_patients(request, pk):
    if request.user.is_superuser:
        p = Patient.objects.filter(regno = pk).first()
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
        context = {
            'users' : d,
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
    
def signout(request):
    logout(request)
    request.session.clear()
    return redirect('signin') 