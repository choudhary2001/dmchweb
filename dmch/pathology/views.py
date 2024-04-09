from django.shortcuts import render, redirect
from .models import *
from counter.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Patient
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pytz
from django.db.models import Min, Max
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
# Get the current time in UTC
current_time_utc = timezone.now()

# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)

@login_required
def fetch_patient_data(request):
    if request.method == 'GET' and 'regno' in request.GET:
        regno = request.GET.get('regno')
        try:
            patient = Patient.objects.filter(regno=regno).first()
            age_parts = []
            if patient.year:
                age_parts.append(f"{patient.year} Y")
            if patient.month:
                age_parts.append(f"{patient.month} M")
            if patient.days:
                age_parts.append(f"{patient.days} D")
            age = ' '.join(age_parts)

            data = {
                'name': patient.name,
                'gender': patient.gender,
                'age': age if age_parts else None,
                # Add more fields as needed
            }
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def fetch_patient_data_details(request):
    if request.method == 'GET' and 'regno' in request.GET:
        regno = request.GET.get('regno')
        try:
            patient = Patient.objects.filter(regno=regno).first()
            pr = Patient_registration.objects.filter(reg_no = patient).first()

            if pr is not None:
                data = {
                    'name': pr.reg_no.name,
                    'bill_no': pr.bill_no,
                    'lab_no': pr.lab_no,
                    'department': pr.department.name,
                    'referby': pr.referby.name,

                    # Add more fields as needed
                }
            else:
                data = {}
            
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def create_patient_registration(request):
    current_time_utc = timezone.now()
    # request.session['user_role'] = 'Registration'

    # Get the Kolkata timezone
    kolkata_timezone = pytz.timezone('Asia/Kolkata')

    # Convert the current time to Kolkata timezone
    current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
    if request.method == 'POST':
        bill_no = request.POST.get('bill_no')
        reg_no = request.POST.get('regno')
        department = request.POST.get('department')
        refer_by = request.POST.get('doctor')
        lab_no = request.POST.get('labno')
        date = request.POST.get('date')
        test_name = request.POST.get('test_name')

        try:
            # Create a patient_registration object
            department = Department.objects.filter(department_id = department).first()
            doctor = Doctor.objects.filter(doctor_id = refer_by).first()
            p = Patient.objects.filter(regno = reg_no).first()
            # tc = Testcode.objects.filter(id = test_name).first()
            patient = Patient_registration.objects.create(
                user = request.user,
                department=department,
                bill_no=bill_no,
                lab_no=lab_no,
                reg_no=p,
                referby=doctor,
                test_name=test_name,
                date=date,
            )
            messages.success(request, 'Patient Added Successfully.')
            return render(request, 'print_patient_reg.html', {"patient" : patient})
        except Exception as e:
            print(e)
            messages.success(request, f"{e}")

    de = Department.objects.all().order_by('-created_at')
    last_patient_pp = Patient_registration.objects.order_by('-created_at').first()
    if last_patient_pp:
        bill_no = int(last_patient_pp.bill_no) + 1
    else:
        bill_no = 1

    t = Testcode.objects.all()

    context = {
        'departments' : de,
        'bill_no' : bill_no,
        'title' : 'Patient Registration',
        'tests' : t,
        'current_time_kolkata' : current_time_kolkata
    }
    return render(request, 'patient_registration.html', context = context)  # Assuming you have a template named patient_registration_form.html


@login_required
def patient_registration_view(request):
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
        patients = Patient_registration.objects.all().order_by('-created_at')
    else:
        patients = Patient_registration.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        patients = patients.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        patients = patients.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        patients = patients.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = patients.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': patients,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
    }
    return render(request, 'patientdata.html', context=context)


@login_required
def patient_registration_view_print(request):
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
        patients = Patient_registration.objects.all().order_by('-created_at')
    else:
        patients = Patient_registration.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        patients = patients.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        patients = patients.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        patients = patients.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = patients.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': patients,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
    }
    return render(request, 'print_patientdata.html', context=context)




@login_required
def update_patient_registration(request, pk):
    patient = get_object_or_404(Patient_registration, pk=pk)

    if request.method == 'POST':
        bill_no = request.POST.get('bill_no')
        reg_no = request.POST.get('regno')
        department = request.POST.get('department')
        refer_by = request.POST.get('doctor')
        lab_no = request.POST.get('labno')
        date = request.POST.get('date')
        test_name = request.POST.get('test_name')
        
        try:
            # Create a patient_registration object
            department = Department.objects.filter(department_id = department).first()
            doctor = Doctor.objects.filter(doctor_id = refer_by).first()
            p = Patient.objects.filter(regno = reg_no).first()
            # tc = Testcode.objects.filter(pk = test_name).first()

            patient.department = department
            patient.referby = doctor
            patient.lab_no = lab_no
            patient.bill_no = bill_no
            patient.test_name = test_name
            patient.date = date
            patient.save()
            messages.success(request, 'Patient Updated Successfully.')
        except Exception as e:
            print(e)
    patient = get_object_or_404(Patient_registration, pk=pk)
    de = Department.objects.all().order_by('-created_at')
    last_patient_pp = Patient_registration.objects.order_by('-created_at').first()
    if last_patient_pp:
        bill_no = int(last_patient_pp.bill_no) + 1
    else:
        bill_no = 1

    t = Testcode.objects.all()

    context = {
        'departments' : de,
        'bill_no' : bill_no,
        'title' : 'Patient Registration',
        'tests' : t,
        'patient' : patient
    }
    return render(request, 'patient_registration_update.html',context=context )

@login_required
def delete_patient_registration(request, pk):
    patient = get_object_or_404(Patient_registration, pk=pk)
    patient.delete()
    return redirect('patient_registration_view')  


# doctor viewsss____________________________

# In views.py



@login_required
def create_doctor(request):
    if request.method == 'POST':
        doctor_name = request.POST.get('doctor_name')
        Doctor.objects.create(doctor_name=doctor_name)
        return redirect('success_url')  # Replace 'success_url' with your success URL
    else:
        # form = DoctorForm()
       return render(request, 'doctor_create_form.html')

@login_required
def update_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor_name = request.POST.get('doctor_name')
        doctor.objects.create(doctor_name=doctor_name)
        return redirect('success_url')  # Replace 'success_url' with your success URL
    else:
        # form = DoctorForm(instance=doctor)
     return render(request, 'doctor_update_form.html')

@login_required
def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        return redirect('success_url')  # Replace 'success_url' with your success URL
    return render(request, 'doctor_confirm_delete.html', {'doctor': doctor})




# -----------------test code --------------

# In views.py


@login_required
def create_testcode(request):
    if request.method == 'POST':
        test_code = request.POST.get('test_code')
        test_name = request.POST.get('test_name')
        testcode = Testcode.objects.create(test_code=test_code, test_name=test_name)
        messages.success(request, 'Test Added Successfully')
    t = Testcode.objects.all()
    context = {
        'tests' : t
    }
    return render(request, 'test.html', context = context)  # Assuming you have a template for creating test code

@login_required
def update_testcode(request, pk):
    testcode = get_object_or_404(Testcode, pk=pk)
    if request.method == 'POST':
        test_code = request.POST.get('test_code')
        test_name = request.POST.get('test_name')
        testcode.test_code = test_code
        testcode.test_name = test_name
        testcode.save()
        messages.success(request, 'Test Updated Successfully.')
    return redirect('create_testcode')

@login_required
def delete_testcode(request, pk):
    testcode = get_object_or_404(Testcode, pk=pk)
    testcode.delete()
    return redirect('create_testcode')



# --------------------------- create test report 1 -------------
# In views.py

@login_required
def create_test_report(request):
    if request.method == 'POST':
        # Extract data from POST request for all fields
        reg_no = request.POST.get('regno')
        print(reg_no)
        data = {}
        for field in Test_report._meta.fields:
            data[field.name] = request.POST.get(field.name)
        print(data)
        # Fetch the corresponding Patient object based on the provided reg_no

        patient = Patient.objects.filter(regno=reg_no).first()
        pr = Patient_registration.objects.filter(reg_no=patient).first()
        print(patient, pr)
        # Assign the patient object to the reg_no field in the data
        data['reg_no'] = patient
        data['patient'] = pr
        data['user'] = request.user
        
        # Create test_report instance
        test_report_obj = Test_report.objects.create(**data)
        messages.success(request, 'Test Report created successfully')
        # Redirect or render a success page as needed
        
    de = Department.objects.all().order_by('-created_at')
    last_patient_pp = Patient_registration.objects.order_by('-created_at').first()
    if last_patient_pp:
        bill_no = int(last_patient_pp.bill_no) + 1
    else:
        bill_no = 1

    t = Testcode.objects.all()

    context = {
        'departments' : de,
        'bill_no' : bill_no,
        'title' : 'Add Test Report',
        'tests' : t
    }
    return render(request, 'add_test_report.html', context=context)

@login_required
def create_test_report_view(request):
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
        tr = Test_report.objects.all().order_by('-created_at')
    else:
        tr = Test_report.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Test Report'
    }
    return render(request, 'test_report_data.html', context=context)

@login_required
def create_test_report_view_print(request):
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
        tr = Test_report.objects.all().order_by('-created_at')
    else:
        tr = Test_report.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Test Report'
    }
    return render(request, 'print_test_report.html', context=context)



@login_required
def update_test_report(request, pk):
    test_report_obj = get_object_or_404(Test_report, pk=pk)
    if request.method == 'POST':
        # Update test_report instance
        for field in Test_report._meta.fields:
            if request.POST.get(field.name):
                setattr(test_report_obj, field.name, request.POST.get(field.name))
        test_report_obj.save()
    counter = 1 
    return render(request, 'update_test_report.html', {'test_report': test_report_obj, 'title' : 'Update Test Report'})  # Assuming you have a template for updating test report

@login_required
def delete_test_report(request, pk):
    test_report_obj = get_object_or_404(Test_report, pk=pk)
    test_report_obj.delete()
    return redirect('create_test_report_view')



# ----------------kUrine test viewss and function -----------


# In views.py

@login_required
def create_urine_test(request):
    if request.method == 'POST':
        # Extract data from POST request for all fields
        reg_no = request.POST.get('regno')

        data = {}
        for field in Urine_test._meta.fields:
            data[field.name] = request.POST.get(field.name)

        patient = Patient.objects.filter(regno=reg_no).first()
        pr = Patient_registration.objects.filter(reg_no=patient).first()
        print(patient, pr)
        # Assign the patient object to the reg_no field in the data
        data['reg_no'] = patient
        data['patient'] = pr
        data['user'] = request.user

        # Create urine_test instance
        urine_test_obj = Urine_test.objects.create(**data)
        messages.success(request, 'Urine Test Added Successfully.')

    return render(request, 'add_urine_test.html', {'title' : 'Urine Test'})  # Assuming you have a template for creating urine test


@login_required
def urine_test_report_view(request):
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
        tr = Urine_test.objects.all().order_by('-created_at')
    else:
        tr = Urine_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Urine Test Report'
    }
    return render(request, 'urine_test_data.html', context=context)


@login_required
def urine_test_report_view_print(request):
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
        tr = Urine_test.objects.all().order_by('-created_at')
    else:
        tr = Urine_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Urine Test Report'
    }
    return render(request, 'print_urine_test.html', context=context)


@login_required
def update_urine_test(request, pk):
    urine_test_obj = get_object_or_404(Urine_test, pk=pk)
    if request.method == 'POST':
        # Update urine_test instance
        for field in Urine_test._meta.fields:
            if request.POST.get(field.name):
                setattr(urine_test_obj, field.name, request.POST.get(field.name))
        urine_test_obj.save()
        messages.success(request, 'Urine Test Updated Successfully.')
    return render(request, 'update_urine_test.html', {'urine': urine_test_obj, 'title' : 'Update Urine Test'})# Assuming you have a template for updating urine test

@login_required
def delete_urine_test(request, pk):
    urine_test_obj = get_object_or_404(Urine_test, pk=pk)
    urine_test_obj.delete()
    return redirect('urine_test_report_view')



# ------------------stool test --------------
# In views.py



# Views for stool_test
@login_required
def create_stool_test(request):
    if request.method == 'POST':
        reg_no = request.POST.get('regno')

        data = {}
        for field in Stool_test._meta.fields:
            data[field.name] = request.POST.get(field.name)

        patient = Patient.objects.filter(regno=reg_no).first()
        pr = Patient_registration.objects.filter(reg_no=patient).first()
        print(patient, pr)
        # Assign the patient object to the reg_no field in the data
        data['reg_no'] = patient
        data['patient'] = pr
        data['user'] = request.user

        # Create urine_test instance

        Stool_test.objects.create(**data)
        messages.success(request, 'Stool test added Successfully.')
    return render(request, 'add_stool_test.html', {'title' : 'Stool Test'})

@login_required
def stool_test_report_view(request):
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
        tr = Stool_test.objects.all().order_by('-created_at')
    else:
        tr = Stool_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Stool Test Report'
    }
    return render(request, 'stool_test_data.html', context=context)


@login_required
def stool_test_report_view_print(request):
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
        tr = Stool_test.objects.all().order_by('-created_at')
    else:
        tr = Stool_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Stool Test Report'
    }
    return render(request, 'print_stool_test.html', context=context)


@login_required
def update_stool_test(request, pk):
    stool_test_obj = get_object_or_404(Stool_test, pk=pk)
    if request.method == 'POST':
        for field in Stool_test._meta.fields:
            if request.POST.get(field.name):
                setattr(stool_test_obj, field.name, request.POST.get(field.name))
        stool_test_obj.save()
    return render(request, 'update_stool_test.html', {'stool': stool_test_obj, 'title' : 'Update Stool Test Report'})

@login_required
def delete_stool_test(request, pk):
    stool_test_obj = get_object_or_404(Stool_test, pk=pk)
    stool_test_obj.delete()
    return redirect('stool_test_report_view')


# --------------------ctest viewss ------------
# In views.py


@login_required
def create_ctest_report(request):
    if request.method == 'POST':
        data = {}
        reg_no = request.POST.get('regno')

        for field in Ctest_report._meta.fields:
            data[field.name] = request.POST.get(field.name)

        patient = Patient.objects.filter(regno=reg_no).first()
        pr = Patient_registration.objects.filter(reg_no=patient).first()
        print(patient, pr)
        # Assign the patient object to the reg_no field in the data
        data['reg_no'] = patient
        data['patient'] = pr
        data['user'] = request.user
        # Create urine_test instance
        Ctest_report.objects.create(**data)
        messages.success(request, 'C Test  Added Successfully.')
    return render(request, 'add_ctest.html', {'title': 'C Test'})


@login_required
def c_test_report_view(request):
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
        tr = Ctest_report.objects.all().order_by('-created_at')
    else:
        tr = Ctest_report.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0
    # for p in patients:
    #     if p.visittype == 'Unknown':
    #         unkown_total += 1
    #     if p.redcard in [True, 'true']:  
    #         if p.redcardtype == 'Red Card':
    #             red_card_total += 1
    #         if p.redcardtype == 'RB Case':
    #             rb_case_total += 1


    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'C Test Report'
    }
    return render(request, 'c_test_data.html', context=context)


@login_required
def c_test_report_view_print(request):
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
        tr = Ctest_report.objects.all().order_by('-created_at')
    else:
        tr = Ctest_report.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'C Test Report'
    }
    return render(request, 'print_ctest_report.html', context=context)



@login_required
def update_ctest_report(request, pk):
    ctest_report_obj = get_object_or_404(Ctest_report, pk=pk)
    if request.method == 'POST':
        for field in Ctest_report._meta.fields:
            if request.POST.get(field.name):
                setattr(ctest_report_obj, field.name, request.POST.get(field.name))
        ctest_report_obj.save()
    return render(request, 'update_ctest_report.html', {'ctest': ctest_report_obj, 'title' : 'Update C Test'})

@login_required
def delete_ctest_report(request, pk):
    ctest_report_obj = get_object_or_404(Ctest_report, pk=pk)
    ctest_report_obj.delete()
    return redirect('c_test_report_view')

# -------------------cbc test viewssss ----------------

# In views.py



@login_required
def create_cbc_test(request):
    if request.method == 'POST':
        reg_no = request.POST.get('regno')

        data = {}
        for field in Cbc_test._meta.fields:
            data[field.name] = request.POST.get(field.name)

        patient = Patient.objects.filter(regno=reg_no).first()
        pr = Patient_registration.objects.filter(reg_no=patient).first()
        print(patient, pr)
        # Assign the patient object to the reg_no field in the data
        data['reg_no'] = patient
        data['patient'] = pr
        data['user'] = request.user

        # Create urine_test instance
        
        Cbc_test.objects.create(**data)
        messages.success(request, 'CBC test added Successfully.')
    return render(request, 'add_cbc_test.html', {'title' : 'CBC Test'})



@login_required
def cbc_test_report_view(request):
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
        tr = Cbc_test.objects.all().order_by('-created_at')
    else:
        tr = Cbc_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'CBC Test Report'
    }
    return render(request, 'cbc_test_data.html', context=context)


@login_required
def cbc_test_report_view_print(request):
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
        tr = Cbc_test.objects.all().order_by('-created_at')
    else:
        tr = Cbc_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'CBC Test Report'
    }
    return render(request, 'print_cbc_test.html', context=context)




@login_required
def update_cbc_test(request, pk):
    cbc_test_obj = get_object_or_404(Cbc_test, pk=pk)
    if request.method == 'POST':
        for field in Cbc_test._meta.fields:
            if request.POST.get(field.name):
                setattr(cbc_test_obj, field.name, request.POST.get(field.name))
        cbc_test_obj.save()
    return render(request, 'update_cbc_test.html', {'cbc': cbc_test_obj, 'title' : 'Update CBC Test'})

@login_required
def delete_cbc_test(request, pk):
    cbc_test_obj = get_object_or_404(Cbc_test, pk=pk)
    cbc_test_obj.delete()
    return redirect('cbc_test_report_view')


# ------------------------serology test viewsss ------------
# In views.py

@login_required
def create_serology_test(request):
    if request.method == 'POST':
        reg_no = request.POST.get('regno')

        data = {}
        for field in Serology_test._meta.fields:
            data[field.name] = request.POST.get(field.name)

        patient = Patient.objects.filter(regno=reg_no).first()
        pr = Patient_registration.objects.filter(reg_no=patient).first()
        print(patient, pr)
        # Assign the patient object to the reg_no field in the data
        data['reg_no'] = patient
        data['patient'] = pr
        # Create urine_test instance
        data['user'] = request.user

        Serology_test.objects.create(**data)
        messages.success(request, 'Serology test added Successfully.')
        
    return render(request, 'add_serology_test.html', {'title': 'Serology Test'})


@login_required
def serology_test_report_view(request):
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
        tr = Serology_test.objects.all().order_by('-created_at')
    else:
        tr = Serology_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Serology Test Report'
    }
    return render(request, 'serology_test_data.html', context=context)


@login_required
def serology_test_report_view_print(request):
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
        tr = Serology_test.objects.all().order_by('-created_at')
    else:
        tr = Serology_test.objects.filter(user = request.user).order_by('-created_at')


    if start_date and end_date:
        # end_date = end_date + timedelta(days=1) 
        # start_date = start_date - timedelta(days=1)
        tr = tr.filter(created_at__range=(start_date, end_date))
    elif start_date:
        # If only start date is provided, include all records for that day
        next_day = start_date + timedelta(days=1)
        tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
    elif end_date:
        tr = tr.filter(created_at__lt=end_date)
    
    
    non_price = 0
    red_card_total = 0
    rb_case_total = 0
    unkown_total = 0

    non_price = red_card_total + rb_case_total + unkown_total
    # Count the total number of patients
    total = tr.count()

    total_amount = (int(total) * 5) - (non_price * 5)


    context = {
        'patients': tr,
        'title': f'Total Patients: {total}',
        'total_amount' : total_amount,
        'title' : 'Serology Test Report'
    }
    return render(request, 'print_serology_test.html', context=context)



@login_required
def update_serology_test(request, pk):
    serology_test_obj = get_object_or_404(Serology_test, pk=pk)
    if request.method == 'POST':
        for field in Serology_test._meta.fields:
            if request.POST.get(field.name):
                setattr(serology_test_obj, field.name, request.POST.get(field.name))
        serology_test_obj.save()
    return render(request, 'update_serology_test.html', {'serology': serology_test_obj, 'title' : 'Update Serology'})

@login_required
def delete_serology_test(request, pk):
    serology_test_obj = get_object_or_404(Serology_test, pk=pk)
    serology_test_obj.delete()
    return redirect('serology_test_report_view')