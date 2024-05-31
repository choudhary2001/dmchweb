from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
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
from django.forms.models import model_to_dict
# Get the current time in UTC
current_time_utc = timezone.now()
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlparse, parse_qs, unquote_plus
from collections import Counter
from django.db.models import Count
from collections import defaultdict
import requests

# Get the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

# Convert the current time to Kolkata timezone
current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
print(current_time_kolkata)

@login_required
def fetch_patient_data(request):
    if request.method == 'GET' and 'regid' in request.GET:
        regid = request.GET.get('regid')
        try:
            # patient = Patient.objects.filter(regid=regid).first()
            patient = Patient.objects.filter(Q(regid=regid) | Q(regnoid=regid)).first()

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
                'mob_no': patient.mobno
                # Add more fields as needed
            }
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

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

            # patient = Patient.objects.filter(Q(regid=regid) | Q(regnoid=regid)).first()
            pr = Patient_registration.objects.filter(reg_no=patient).first()

            if pr is not None:
                department_name = None
                try:
                    if pr.department is not None:
                        department_name = pr.department.name
                except Exception as e:
                    print(e)
                    department_name = None

                refer_by_name = None
                try:
                    if pr.referby is not None:
                        refer_by_name = pr.referby.name
                except Exception as e:
                    print(e)
                    refer_by_name = None

                t = Test_report.objects.filter(patient = pr).first()
                test_report = {
                    'available' : False
                }
                if t is not None:
                    test_report = {
                        'available' : True,
                        'id' : t.id
                    }

                u = Urine_test.objects.filter(patient = pr).first()
                urine_report = {
                    'available' : False
                }
                if u is not None:
                    urine_report = {
                        'available' : True,
                        'id' : u.id
                    }

                st = Stool_test.objects.filter(patient = pr).first()
                stool_report = {
                    'available' : False
                }
                if st is not None:
                    stool_report = {
                        'available' : True,
                        'id' : st.id
                    }

                ct = Ctest_report.objects.filter(patient = pr).first()
                ct_report = {
                    'available' : False
                }
                if ct is not None:
                    ct_report = {
                        'available' : True,
                        'id' : ct.id
                    }

                cbc = Cbc_test.objects.filter(patient = pr).first()
                cbc_report = {
                    'available' : False
                }
                if cbc is not None:
                    ct_report = {
                        'available' : True,
                        'id' : cbc.id
                    }

                sr = Serology_test.objects.filter(patient = pr).first()
                sr_report = {
                    'available' : False
                }
                if sr is not None:
                    sr_report = {
                        'available' : True,
                        'id' : sr.id
                    }

                data = {
                    'name': pr.reg_no.name,
                    'bill_no': pr.bill_no,
                    'lab_no': pr.lab_no,
                    'department': department_name,
                    'referby': refer_by_name,
                    'test_report' : test_report,
                    'urine_report' : urine_report,
                    'stool_report' : stool_report,
                    'ct_report' : ct_report,
                    'cbc_report' : cbc_report,
                    'sr_report' : sr_report,
                    # Add more fields as needed
                }
            else:
                data = {}

            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

import re

def extract_duration(duration_str):
    # Regular expression pattern to find integers
    pattern = r'\d+'

    # Extract integers from the string
    numbers = re.findall(pattern, duration_str)

    # Initialize variables for years, months, and days
    years = months = days = 0

    # If integers are found, assign them to corresponding variables
    if numbers:
        years = int(numbers[0]) if len(numbers) > 0 else 0
        months = int(numbers[1]) if len(numbers) > 1 else 0
        days = int(numbers[2]) if len(numbers) > 2 else 0

    return years, months, days


@login_required
def create_patient_registration(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':
        current_time_utc = timezone.now()
        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        if request.method == 'POST':
            bill_no = request.POST.get('bill_no')
            reg_no = request.POST.get('regid')
            department = request.POST.get('department')
            refer_by = request.POST.get('doctor')
            lab_no = request.POST.get('labno')
            date = request.POST.get('date')
            test_name = request.POST.get('test_name')
            patient_name = request.POST.get('patient_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            mob_no = request.POST.get('mob_no', None)

            try:
                # Create a patient_registration object
                department = PathologyDepartment.objects.filter(department_id = department).first()
                doctor = PathologyDoctor.objects.filter(doctor_id = refer_by).first()
                try:
                    p = Patient.objects.filter(regid = reg_no).first()
                except Exception as e:
                    try:
                        p = Patient.objects.filter(regnoid = reg_no).first()
                    except Exception as e:
                        print(e)
                        p = None
                # tc = Testcode.objects.filter(id = test_name).first()
                if p is not None:
                    # if mob_no is not None:
                    #     p.mobno = mob_no
                    #     p.save()
                    patient = Patient_registration.objects.create(
                        user = request.user,
                        department=department,
                        bill_no=bill_no,
                        lab_no=lab_no,
                        reg_no=p,
                        referby=doctor,
                        test_name=test_name,
                        date=date
                    )
                else:
                    years, months, days = extract_duration(age)
                    pp = Patient.objects.create(
                        regnoid = reg_no,
                        user = request.user,
                        name = patient_name,
                        gender = gender,
                        year = years,
                        month = months,
                        days = days,
                        mobno = mob_no,
                        de = 'Pathology'
                    )
                    # p.save()
                    patient = Patient_registration.objects.create(
                        user = request.user,
                        department=department,
                        bill_no=bill_no,
                        lab_no=lab_no,
                        reg_no=pp,
                        referby=doctor,
                        test_name=test_name,
                        patient_name=patient_name,
                        gender=gender,
                        age=age,
                        date=date,
                    )
                messages.success(request, 'Patient Added Successfully.')
                return render(request, 'print_patient_reg.html', {"patient" : patient})
            except Exception as e:
                print(e)
                messages.success(request, f"{e}")

        de = PathologyDepartment.objects.all().order_by('-created_at')
        do = PathologyDoctor.objects.all().order_by('-created_at')
        last_patient_pp = Patient_registration.objects.order_by('-created_at').first()
        if last_patient_pp:
            bill_no = int(last_patient_pp.bill_no) + 1
        else:
            bill_no = 1

        t = Testcode.objects.all()

        context = {
            'departments' : de,
            'doctors' : do,
            'bill_no' : bill_no,
            'title' : 'Patient Registration',
            'tests' : t,
            'current_time_kolkata' : current_time_kolkata
        }
        return render(request, 'patient_registration.html', context = context)  # Assuming you have a template named patient_registration_form.html
    else:
        logout(request)
        return redirect('signin') 

@login_required
def patient_registration_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department_id = request.GET.get('department')
        total = 0

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
        
        if start_date_str or end_date_str or department_id:
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
            
            # Count the total number of patients
            if department_id != None:
                depart = PathologyDepartment.objects.filter(department_id =department_id).first()
                if department_id != 'All':
                    patients = patients.filter(department=depart)
                    
            total = patients.count()
            
        else:
            patients = {}


        context = {
            'patients': patients,
            'title': f'Total Patients: {len(Patient_registration.objects.all())}',
            'end_date_str' : end_date_str,
            'start_date_str' : start_date_str,
            'departments' : PathologyDepartment.objects.all().order_by('name')

        }
        return render(request, 'patientdata.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def patient_registration_view_data(request):
    if request.user.is_superuser or request.session.get('user_role') == 'Pathology':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department = request.GET.get('department')

        # Convert the date strings to datetime objects
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None

        if request.user.is_superuser:
            tr = Patient_registration.objects.all().order_by('-created_at')
        else:
            tr = Patient_registration.objects.filter(user = request.user).order_by('-created_at')


        # tr = Patient_registration.objects.all().order_by('-created_at')

        search_query = request.GET.get('searchValue')

        # Date range filter
        if start_date and end_date:
            tr = tr.filter(created_at__range=(start_date, end_date))
        elif start_date:
            next_day = start_date + timedelta(days=1)
            tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
        elif end_date:
            tr = tr.filter(created_at__lt=end_date)

        # Count the total number of records
        total = tr.count()

        # Search filter
        if search_query:
            tr = tr.filter(
                Q(patient_name__icontains=search_query) |
                Q(reg_no__regid__icontains=search_query) |
                Q(reg_no__regnoid__icontains=search_query) |
                Q(reg_no__mobno__icontains=search_query) |
                Q(bill_no__icontains=search_query) |
                Q(test_name__icontains=search_query) |
                Q(lab_no__icontains=search_query) |
                Q(referby__name__icontains=search_query) |
                Q(department__name__icontains=search_query)
            )

        # Pagination
        page = request.GET.get('draw', 1)
        print(page)
        paginator = Paginator(tr, 10)  # Show 10 records per page
        try:
            patients = paginator.page(page)
        except PageNotAnInteger:
            patients = paginator.page(1)
        except EmptyPage:
            patients = paginator.page(paginator.num_pages)

        # Serialize patients data
        patients_data = []
        for patient in patients:
            patient_doctor = patient.referby.name if patient.referby else ''
            patient_department = patient.department.name if patient.department else ''
            patient_mobile = patient.reg_no.mobno if patient.reg_no else ''
            patient_reg_no = patient.reg_no.regnoid if patient.reg_no and patient.reg_no.de == 'Pathology' else patient.reg_no.regid

            patients_data.append({
                'id': patient.id,
                'regid': patient_reg_no,
                'name': patient.reg_no.name,
                'mobile': patient_mobile,
                'test_name': patient.test_name,
                'bill_no': patient.bill_no,
                'lab_no': patient.lab_no,
                'department': patient_department,
                'refer_by': patient_doctor,
                'date': patient.created_at,
            })


        data = {
            'patients': patients_data,
            'has_next': patients.has_next(),
            'has_prev': patients.has_previous(),
            'draw': request.GET.get('draw'),  # Echo back the draw parameter
            'recordsTotal': total,  # Total records without filtering
            'recordsFiltered': paginator.count,  # Total records after filtering (for now)
            
        }
        return JsonResponse(data)
    else:
        logout(request)
        return redirect('signin')


@login_required
def patient_registration_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department_id = request.GET.get('department', None)

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
        total = 0

        if start_date_str or end_date_str or department_id:
        
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
            if department_id != None:
                depart = PathologyDepartment.objects.filter(department_id =department_id).first()
                if department_id != 'All':
                    patients = patients.filter(department=depart)
        
            total = patients.count()
            
        else:
            patients = {}

        context = {
            'patients': patients,
            'title': f'Total Patients: {total}',
            'start_date_str' : start_date_str,
            'end_date_str' : end_date_str,
            'departments' : PathologyDepartment.objects.all().order_by('name')
        }
        return render(request, 'print_patientdata.html', context=context)

    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_patient_registration(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        patient = get_object_or_404(Patient_registration, pk=pk)

        if request.method == 'POST':
            bill_no = request.POST.get('bill_no')
            reg_no = request.POST.get('regid')
            department = request.POST.get('department')
            refer_by = request.POST.get('doctor')
            lab_no = request.POST.get('labno')
            date = request.POST.get('date')
            test_name = request.POST.get('test_name')
            patient_name = request.POST.get('patient_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            mob_no = request.POST.get('mob_no')
            
            try:
                # Create a patient_registration object
                department = PathologyDepartment.objects.filter(department_id = department).first()
                doctor = PathologyDoctor.objects.filter(doctor_id = refer_by).first()
                p = Patient.objects.filter(regid = reg_no).first()
                # tc = Testcode.objects.filter(pk = test_name).first()

                patient.department = department
                patient.referby = doctor
                patient.lab_no = lab_no
                patient.bill_no = bill_no
                patient.test_name = test_name
                patient.date = date
                patient.save()
                p = Patient.objects.filter(regid = reg_no, de='Pathology').first()
                if p is not None:
                    p.name = patient_name
                    p.gender = gender
                    years, months, days = extract_duration(age)
                    p.year = years
                    p.month = months
                    p.days = days
                    p.mobno = mob_no
                    p.save()
                messages.success(request, 'Patient Updated Successfully.')
            except Exception as e:
                print(e)
        patient = get_object_or_404(Patient_registration, pk=pk)
        de = PathologyDepartment.objects.all().order_by('-created_at')
        last_patient_pp = Patient_registration.objects.order_by('-created_at').first()
        if last_patient_pp:
            bill_no = int(last_patient_pp.bill_no) + 1
        else:
            bill_no = 1

        t = Testcode.objects.all()
        do = PathologyDoctor.objects.all().order_by('-created_at')

        context = {
            'departments' : de,
            'doctors' : do,
            'bill_no' : bill_no,
            'title' : 'Patient Registration',
            'tests' : t,
            'patient' : patient
        }
        return render(request, 'patient_registration_update.html',context=context )

    else:
        logout(request)
        return redirect('signin') 

@login_required
def delete_patient_registration(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        patient = get_object_or_404(Patient_registration, pk=pk)

        patient.delete()
        return redirect('patient_registration_view')  
    else:
        logout(request)
        return redirect('signin') 

# doctor viewsss____________________________

# In views.py




@login_required
def departments(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == "POST":
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            d = PathologyDepartment(name = department, room_no = room_no)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = PathologyDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : d,
            'title' : 'Departments'
        }
        return render(request, 'pathology_departments.html', context = context)
    else:
        logout(request)
        return redirect('signin') 

    
@login_required
def departments_update(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == "POST":
            d = PathologyDepartment.objects.filter(department_id =department_id).first()
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            print(room_no)
            dc = PathologyDepartment.objects.filter(name = department).first()
            if not dc or dc.name == department:
                d.name = department
                d.room_no = room_no
                d.save()
                messages.success(request, 'Department updated successfully.')
            else:
                messages.error(request, 'Department name already exists.')

        return redirect('pathology_departments')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def departments_delete(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        d = PathologyDepartment.objects.filter(department_id =department_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('pathology_departments')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def doctors(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == "POST":
            doctor = request.POST['doctor']
            # department = request.POST['department']
            d = PathologyDoctor(name = doctor)
            d.save()
            messages.success(request, 'Doctor added successfully.')
        d = PathologyDoctor.objects.all().order_by('created_at')
        de = PathologyDepartment.objects.all().order_by('created_at')

        context = {
            'doctors' : d,
            'departments' : de,
            'title' : "Doctors"
        }
        return render(request, 'pathology_doctor.html', context = context)

    else:
        logout(request)
        return redirect('signin')  

@login_required
def doctors_update(request, doctor_id):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == "POST":
            d = PathologyDoctor.objects.filter(doctor_id =doctor_id).first()
            doctor = request.POST['doctor']
            # department = request.POST['department']
            # de = PathologyDepartment.objects.filter(department_id =department).first()

            dc = PathologyDoctor.objects.filter(name = doctor).all()
            # if not dc:
            d.name = doctor
            d.save()
            messages.success(request, 'Doctor updated successfully.')
            # else:
            #     messages.error(request, 'Doctor name already exists.')
        return redirect('pathology_doctors')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def doctors_delete(request, doctor_id):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        d = PathologyDoctor.objects.filter(doctor_id =doctor_id).first()
        d.delete()
        messages.success(request, 'Doctor updated successfully.')

        return redirect('pathology_doctors')
    else:
        logout(request)
        return redirect('signin') 
    


# -----------------test code --------------

# In views.py


@login_required
def create_testcode(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_testcode(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        testcode = get_object_or_404(Testcode, pk=pk)
        if request.method == 'POST':
            test_code = request.POST.get('test_code')
            test_name = request.POST.get('test_name')
            testcode.test_code = test_code
            testcode.test_name = test_name
            testcode.save()
            messages.success(request, 'Test Updated Successfully.')
        return redirect('create_testcode')
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_testcode(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        testcode = get_object_or_404(Testcode, pk=pk)
        testcode.delete()
        return redirect('create_testcode')

    else:
        logout(request)
        return redirect('signin') 


# --------------------------- create test report 1 -------------
# In views.py

@login_required
def create_test_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == 'POST':
            # Extract data from POST request for all fields
            reg_no = request.POST.get('regid')
            print(reg_no)
            data = {}
            for field in Test_report._meta.fields:
                data[field.name] = request.POST.get(field.name)
            print(data)
            # Fetch the corresponding Patient object based on the provided reg_no

            try:
                regid_int = int(reg_no)
                # If no exception is raised, it means regid is an integer
                patient = Patient.objects.filter(Q(regid=regid_int) | Q(regnoid=reg_no)).first()
            except ValueError:
                # If regid cannot be converted to an integer, treat it as a varchar
                patient = Patient.objects.filter(regnoid=reg_no).first()

            pr = Patient_registration.objects.filter(reg_no=patient).first()
            print(patient, pr)
            if pr is not None:
                # Assign the patient object to the reg_no field in the data
                data['reg_no'] = patient
                data['patient'] = pr
                data['user'] = request.user
                
                # Create test_report instance
                test_report_obj = Test_report.objects.create(**data)
                # test_report_obj = None
                messages.success(request, 'Test Report created successfully')
                # Redirect or render a success page as needed
                try:
                    mob_no = pr.reg_no.mobno
                    # mob_no = '7654531678'
                    if mob_no:
                        url = "https://www.fast2sms.com/dev/bulkV2"

                        payload = (
                            f"sender_id=DMCH&"
                            f"message=169254&"
                            f"variables_values={pr.reg_no.name}|{mob_no}|{mob_no}&"
                            f"route=dlt&"
                            f"flash=1&"
                            f"numbers={mob_no}"
                        )
                        print(payload)

                        headers = {
                            'authorization': "XWNHkDJmUba43l29xi1QCoI8ZsqBnGzgLfuEYS5p7AdhMc6eOrd7iLOaZQy21eosWJGHlFuI4TM3D9kV",
                            'Content-Type': "application/x-www-form-urlencoded",
                            'Cache-Control': "no-cache",
                        }

                        response = requests.request("POST", url, data=payload, headers=headers)
                        print(response.text)

                except Exception as e:
                    print(e)

                return render(request, 'print_report_test_report.html', {"test_report" : test_report_obj})

            else:
                messages.success(request, 'Please complete Registration using this id then create report.')
                
        de = PathologyDepartment.objects.all().order_by('-created_at')
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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def create_test_report_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department_id = request.GET.get('department')
        department = None
        total = 0

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

        if start_date_str or end_date_str or department_id:
        
            # Filter patients based on the provided date range
            if request.user.is_superuser:
                tr = Test_report.objects.all().order_by('-created_at')
            else:
                tr = Test_report.objects.filter(user = request.user).order_by('-created_at')


            if start_date and end_date:
                tr = tr.filter(created_at__range=(start_date, end_date))
            elif start_date:
                next_day = start_date + timedelta(days=1)
                tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
            elif end_date:
                tr = tr.filter(created_at__lt=end_date)
            
            
            # Count the total number of patients
            total = tr.count()
            
            
            if department_id != None:
                if department_id != 'All':
                    de = PathologyDepartment.objects.filter(department_id = department_id).first()
                    pr = Patient_registration.objects.filter(department = de).all()
                    print(de)
                    if de:
                        # tr = tr.filter(department = de, de = None)
                        # print(tr)
                        # department = de.name
                        tr = tr.filter(patient__department=de)
                        department = de.name

        else:
            tr = {}

        d = PathologyDepartment.objects.all()


        context = {
            'patients': tr,
            'title' : f'Test Report :  {len(Test_report.objects.all())}',
            'department' : department,
            'departments' : d,
            'end_date_str' : end_date_str,
            'start_date_str' : start_date_str
        }
        return render(request, 'test_report_data.html', context=context)
    else:
        logout(request)
        return redirect('signin') 



@login_required
def create_test_report_view_data(request):
    if request.user.is_superuser or request.session.get('user_role') == 'Pathology':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department = request.GET.get('department')

        # Convert the date strings to datetime objects
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None

        tr = Test_report.objects.all().order_by('-created_at')

        search_query = request.GET.get('searchValue')

        # Date range filter
        if start_date and end_date:
            tr = tr.filter(created_at__range=(start_date, end_date))
        elif start_date:
            next_day = start_date + timedelta(days=1)
            tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
        elif end_date:
            tr = tr.filter(created_at__lt=end_date)

        # Count the total number of records
        total = tr.count()

        # Search filter
        if search_query:
            tr = tr.filter(
                Q(patient__patient_name__icontains=search_query) |
                Q(patient__bill_no__icontains=search_query) |
                Q(patient__test_name__icontains=search_query) |
                Q(patient__lab_no__icontains=search_query) |
                Q(patient__referby__name__icontains=search_query) |
                Q(patient__department__name__icontains=search_query)
            )

        # Pagination
        page = request.GET.get('draw', 1)
        print(page)
        paginator = Paginator(tr, 10)  # Show 10 records per page
        try:
            patients = paginator.page(page)
        except PageNotAnInteger:
            patients = paginator.page(1)
        except EmptyPage:
            patients = paginator.page(paginator.num_pages)

        # Serialize patients data
        patients_data = []
        for patient in patients:
            patient_doctor = patient.patient.referby.name if patient.patient.referby else ''
            patient_department = patient.patient.department.name if patient.patient.department else ''
            patient_reg_no = patient.reg_no.regnoid if patient.reg_no and patient.reg_no.de == 'Pathology' else patient.reg_no.regid

            patients_data.append({
                'test_report_id': patient.test_report_id,
                'id': patient.id,
                'regid': patient_reg_no,
                'name': patient.patient.patient_name,
                'test_name': patient.patient.test_name,
                'bill_no': patient.patient.bill_no,
                'lab_no': patient.patient.lab_no,
                'department': patient_department,
                'refer_by': patient_doctor,
                'plasma_glucode_fasting': patient.palsma_glucose_fasting,
                'plasma_glucose_pp': patient.palsma_glucose_pp,
                'blood_sugar_random': patient.blood_sugar_random,
                'blood_ures': patient.blood_ures,
                'serum_creainine': patient.serun_creatinine,
                'date': patient.created_at,
            })

        data = {
            'patients': patients_data,
            'has_next': patients.has_next(),
            'has_prev': patients.has_previous(),
            'draw': request.GET.get('draw'),  # Echo back the draw parameter
            'recordsTotal': total,  # Total records without filtering
            'recordsFiltered': paginator.count,  # Total records after filtering (for now)
        }
        return JsonResponse(data)
    else:
        logout(request)
        return redirect('signin')

@login_required
def create_test_report_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department_id = request.GET.get('department')
        non_price = 0
        red_card_total = 0
        rb_case_total = 0
        unkown_total = 0
        department = None
        total = 0
        total_amount = 0
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
        
        if start_date_str or end_date_str or department_id:
            # Filter patients based on the provided date range
            if request.user.is_superuser:
                tr = Test_report.objects.all().order_by('-created_at')
            else:
                tr = Test_report.objects.filter(user = request.user).order_by('-created_at')

            if start_date and end_date:
                tr = tr.filter(created_at__range=(start_date, end_date))
            elif start_date:
                # If only start date is provided, include all records for that day
                next_day = start_date + timedelta(days=1)
                tr = tr.filter(created_at__gte=start_date, created_at__lt=next_day)
            elif end_date:
                tr = tr.filter(created_at__lt=end_date)
            
            
            non_price = red_card_total + rb_case_total + unkown_total
            # Count the total number of patients
            total = tr.count()

            total_amount = (int(total) * 5) - (non_price * 5)
            
            if department_id != None:
                if department_id != 'All':
                    de = PathologyDepartment.objects.filter(department_id = department_id).first()
                    pr = Patient_registration.objects.filter(department = de).all()
                    print(de)
                    if de:
                        # tr = tr.filter(department = de, de = None)
                        # print(tr)
                        # department = de.name
                        tr = tr.filter(patient__department=de)
                        department = de.name

        else:
            tr = {}

        d = PathologyDepartment.objects.all()


        context = {
            'patients': tr,
            'title': f'Total Patients: {total}',
            'total_amount' : total_amount,
            'title' : 'Test Report',
            'department' : department,
            'departments' : d,

        }
        return render(request, 'print_test_report.html', context=context)

    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_test_report(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':
        test_report_obj = get_object_or_404(Test_report, pk=pk)
        if request.method == 'POST':
            for field in Test_report._meta.fields:
                if request.POST.get(field.name):
                    setattr(test_report_obj, field.name, request.POST.get(field.name))
            test_report_obj.save()
        counter = 1 
        return render(request, 'update_test_report.html', {'test_report': test_report_obj, 'title' : 'Update Test Report'})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_test_report(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        test_report_obj = get_object_or_404(Test_report, pk=pk)
        test_report_obj.delete()
        return redirect('create_test_report_view')
    else:
        logout(request)
        return redirect('signin') 



# ----------------kUrine test viewss and function -----------


# In views.py

@login_required
def create_urine_test(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == 'POST':
            # Extract data from POST request for all fields
            reg_no = request.POST.get('regid')

            data = {}
            for field in Urine_test._meta.fields:
                data[field.name] = request.POST.get(field.name)


            try:
                regid_int = int(reg_no)
                # If no exception is raised, it means regid is an integer
                patient = Patient.objects.filter(Q(regid=regid_int) | Q(regnoid=reg_no)).first()
            except ValueError:
                # If regid cannot be converted to an integer, treat it as a varchar
                patient = Patient.objects.filter(regnoid=reg_no).first()

            pr = Patient_registration.objects.filter(reg_no=patient).first()
            print(patient, pr)
            if pr is not None:
                # Assign the patient object to the reg_no field in the data
                data['reg_no'] = patient
                data['patient'] = pr
                data['user'] = request.user

                # Create urine_test instance
                urine_test_obj = Urine_test.objects.create(**data)
                messages.success(request, 'Urine Test Added Successfully.')
                return render(request, 'print_report_urine_test.html', {"urine" : urine_test_obj})
            else:
                messages.success(request, 'Please complete Registration using this id then create report.')
                
        return render(request, 'add_urine_test.html', {'title' : 'Urine Test'})  # Assuming you have a template for creating urine test
    else:
        logout(request)
        return redirect('signin') 



@login_required
def urine_test_report_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 



@login_required
def urine_test_report_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_urine_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        urine_test_obj = get_object_or_404(Urine_test, pk=pk)
        if request.method == 'POST':
            # Update urine_test instance
            for field in Urine_test._meta.fields:
                if request.POST.get(field.name):
                    setattr(urine_test_obj, field.name, request.POST.get(field.name))
            urine_test_obj.save()
            messages.success(request, 'Urine Test Updated Successfully.')
        return render(request, 'update_urine_test.html', {'urine': urine_test_obj, 'title' : 'Update Urine Test'})# Assuming you have a template for updating urine test
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_urine_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        urine_test_obj = get_object_or_404(Urine_test, pk=pk)
        urine_test_obj.delete()
        return redirect('urine_test_report_view')
    else:
        logout(request)
        return redirect('signin') 



# ------------------stool test --------------
# In views.py



# Views for stool_test
@login_required
def create_stool_test(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == 'POST':
            reg_no = request.POST.get('regid')

            data = {}
            for field in Stool_test._meta.fields:
                data[field.name] = request.POST.get(field.name)

            # patient = Patient.objects.filter(regid=reg_no).first()

            try:
                regid_int = int(reg_no)
                # If no exception is raised, it means regid is an integer
                patient = Patient.objects.filter(Q(regid=regid_int) | Q(regnoid=reg_no)).first()
            except ValueError:
                # If regid cannot be converted to an integer, treat it as a varchar
                patient = Patient.objects.filter(regnoid=reg_no).first()

            pr = Patient_registration.objects.filter(reg_no=patient).first()
            print(patient, pr)
            if pr is not None:
                # Assign the patient object to the reg_no field in the data
                data['reg_no'] = patient
                data['patient'] = pr
                data['user'] = request.user

                # Create urine_test instance

                stool_test_obj = Stool_test.objects.create(**data)
                messages.success(request, 'Stool test added Successfully.')
                return render(request, 'print_report_stool_test.html', {"stool" : stool_test_obj})
            else:
                messages.success(request, 'Please complete Registration using this id then create report.')
                
        return render(request, 'add_stool_test.html', {'title' : 'Stool Test'})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def stool_test_report_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def stool_test_report_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_stool_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        stool_test_obj = get_object_or_404(Stool_test, pk=pk)
        if request.method == 'POST':
            for field in Stool_test._meta.fields:
                if request.POST.get(field.name):
                    setattr(stool_test_obj, field.name, request.POST.get(field.name))
            stool_test_obj.save()
        return render(request, 'update_stool_test.html', {'stool': stool_test_obj, 'title' : 'Update Stool Test Report'})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_stool_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        stool_test_obj = get_object_or_404(Stool_test, pk=pk)
        stool_test_obj.delete()
        return redirect('stool_test_report_view')

    else:
        logout(request)
        return redirect('signin') 

# --------------------ctest viewss ------------
# In views.py


@login_required
def create_ctest_report(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == 'POST':
            data = {}
            reg_no = request.POST.get('regid')

            for field in Ctest_report._meta.fields:
                data[field.name] = request.POST.get(field.name)

            # patient = Patient.objects.filter(regid=reg_no).first()

            try:
                regid_int = int(reg_no)
                # If no exception is raised, it means regid is an integer
                patient = Patient.objects.filter(Q(regid=regid_int) | Q(regnoid=reg_no)).first()
            except ValueError:
                # If regid cannot be converted to an integer, treat it as a varchar
                patient = Patient.objects.filter(regnoid=reg_no).first()

            pr = Patient_registration.objects.filter(reg_no=patient).first()
            print(patient, pr)
            if pr is not None:
                # Assign the patient object to the reg_no field in the data
                data['reg_no'] = patient
                data['patient'] = pr
                data['user'] = request.user
                # Create urine_test instance
                ctest_test_obj = Ctest_report.objects.create(**data)
                messages.success(request, 'H.S.F.   Added Successfully.')
                return render(request, 'print_report_ctest_report.html', {"ctest" : ctest_test_obj})
            else:
                messages.success(request, 'Please complete Registration using this id then create report.')
                
        return render(request, 'add_ctest.html', {'title': 'H.S.F. '})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def c_test_report_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
            'title' : 'H.S.F.  Report'
        }
        return render(request, 'c_test_data.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def c_test_report_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
            'title' : 'H.S.F.  Report'
        }
        return render(request, 'print_ctest_report.html', context=context)
    else:
        logout(request)
        return redirect('signin') 



@login_required
def update_ctest_report(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        ctest_report_obj = get_object_or_404(Ctest_report, pk=pk)
        if request.method == 'POST':
            for field in Ctest_report._meta.fields:
                if request.POST.get(field.name):
                    setattr(ctest_report_obj, field.name, request.POST.get(field.name))
            ctest_report_obj.save()
        return render(request, 'update_ctest_report.html', {'ctest': ctest_report_obj, 'title' : 'Update H.S.F. '})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_ctest_report(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        ctest_report_obj = get_object_or_404(Ctest_report, pk=pk)
        ctest_report_obj.delete()
        return redirect('c_test_report_view')
    else:
        logout(request)
        return redirect('signin') 

# -------------------cbc test viewssss ----------------

# In views.py



@login_required
def create_cbc_test(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == 'POST':
            reg_no = request.POST.get('regid')

            data = {}
            for field in Cbc_test._meta.fields:
                data[field.name] = request.POST.get(field.name)

            # patient = Patient.objects.filter(regid=reg_no).first()

            try:
                regid_int = int(reg_no)
                # If no exception is raised, it means regid is an integer
                patient = Patient.objects.filter(Q(regid=regid_int) | Q(regnoid=reg_no)).first()
            except ValueError:
                # If regid cannot be converted to an integer, treat it as a varchar
                patient = Patient.objects.filter(regnoid=reg_no).first()

            pr = Patient_registration.objects.filter(reg_no=patient).first()
            print(patient, pr)
            if pr is not None:
                # Assign the patient object to the reg_no field in the data
                data['reg_no'] = patient
                data['patient'] = pr
                data['user'] = request.user

                # Create urine_test instance
                
                cbc_test_obj = Cbc_test.objects.create(**data)
                messages.success(request, 'CBC test added Successfully.')
                return render(request, 'print_report_cbc_test.html', {"cbc" : cbc_test_obj})
            else:
                messages.success(request, 'Please complete Registration using this id then create report.')
                
        return render(request, 'add_cbc_test.html', {'title' : 'CBC Test'})
    else:
        logout(request)
        return redirect('signin') 



@login_required
def cbc_test_report_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def cbc_test_report_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 




@login_required
def update_cbc_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        cbc_test_obj = get_object_or_404(Cbc_test, pk=pk)
        if request.method == 'POST':
            for field in Cbc_test._meta.fields:
                if request.POST.get(field.name):
                    setattr(cbc_test_obj, field.name, request.POST.get(field.name))
            cbc_test_obj.save()
        return render(request, 'update_cbc_test.html', {'cbc': cbc_test_obj, 'title' : 'Update CBC Test'})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_cbc_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':
        cbc_test_obj = get_object_or_404(Cbc_test, pk=pk)
        cbc_test_obj.delete()
        return redirect('cbc_test_report_view')

    else:
        logout(request)
        return redirect('signin') 

# ------------------------serology test viewsss ------------
# In views.py

@login_required
def create_serology_test(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        if request.method == 'POST':
            reg_no = request.POST.get('regid')

            data = {}
            for field in Serology_test._meta.fields:
                data[field.name] = request.POST.get(field.name)

            patient = Patient.objects.filter(regid=reg_no).first()
            
            pr = Patient_registration.objects.filter(reg_no=patient).first()
            print(patient, pr)
            if pr is not None:
                # Assign the patient object to the reg_no field in the data
                data['reg_no'] = patient
                data['patient'] = pr
                # Create urine_test instance
                data['user'] = request.user

                serology_test_obj = Serology_test.objects.create(**data)
                messages.success(request, 'Serology test added Successfully.')
                return render(request, 'print_report_serology_test.html', {"serology" : serology_test_obj})
            else:
                messages.success(request, 'Please complete Registration using this id then create report.')
                
        return render(request, 'add_serology_test.html', {'title': 'Serology Test'})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def serology_test_report_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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
    else:
        logout(request)
        return redirect('signin') 


@login_required
def serology_test_report_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

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

    else:
        logout(request)
        return redirect('signin') 


@login_required
def update_serology_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        serology_test_obj = get_object_or_404(Serology_test, pk=pk)
        if request.method == 'POST':
            for field in Serology_test._meta.fields:
                if request.POST.get(field.name):
                    setattr(serology_test_obj, field.name, request.POST.get(field.name))
            serology_test_obj.save()
        return render(request, 'update_serology_test.html', {'serology': serology_test_obj, 'title' : 'Update Serology'})
    else:
        logout(request)
        return redirect('signin') 


@login_required
def delete_serology_test(request, pk):
    if request.user.is_superuser or request.session['user_role'] == 'Pathology':

        serology_test_obj = get_object_or_404(Serology_test, pk=pk)
        serology_test_obj.delete()
        return redirect('serology_test_report_view')
    else:
        logout(request)
        return redirect('signin') 


def find_user_report(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        patients = Patient.objects.filter(mobno=mobile).all()
        print(patients)
        test_reports = []
        for patient in patients:
            print(Patient_registration.objects.filter(reg_no = patient).all())
            pr = Patient_registration.objects.filter(reg_no = patient).all()
            for p in pr:
                print(Test_report.objects.filter(patient=p).all())
                test_reports.extend(Test_report.objects.filter(patient=p).all())
                print(test_reports)
        context = {
            'test_reports': test_reports
        }
        return render(request, 'counter/test_report.html', context=context)
    else:
        return redirect('/home/')


categories = [
    {
        "category": "Immuno Assay (Thyroid)",
        "subcategories": [
            "TSH", "T3", "T4", "FT3", "FT4", "LH", "FSH",
            "Prolectin", "CA-125", "PSA", "Anti CCP",
            "Vitamin B12", "Vitamin D3", "AMH"
        ]
    },
    {
        "category": "Hematology",
        "subcategories": ["CBC", "HbA1c", "ESR", "BT", "CT", "MP"]
    },
    {
        "category": "Serology",
        "subcategories": [
            "HIV", "HBSAg", "HCV", "Widal", "Malaria",
            "Dengue Test", "Typhoid Test", "VDRL", "RPR"
        ]
    },
    {
        "category": "Cytopathology",
        "subcategories": ["PAP Smear", "FNAC", "CSF", "Pleural Fluid", "Ascitic Fluid"]
    },
    {
        "category": "Histopathology",
        "subcategories": ["Biopsy"]
    },
    {
        "category": "Bio-Chemistry",
        "subcategories": [
            "Sugar", "B. Urea", "S. Creatinine", "S. Uric Acid",
            "D. Bilirubin", "T. Bilirubin", "SGPT (ALT)",
            "SGOT (AST)", "T. Protein", "Albumin", "ALP", "GGT",
            "Cholesterol", "TGL", "HDL", "LDL", "VLDL", "CRP",
            "ASO", "RA Factor", "Amylase", "Lipase", "HbA1c",
            "Calcium", "S. Electrolytes", "Ferritin", "Acid Phosphatase",
            "Iron", "TIBC (Total Iron Binding Capacity)",
            "Magnesium", "Phosphorous", "CPK", "CK-MB", "CK-NAC", "LFT", "KFT", "TLP"
        ]
    }
]

# Create the test name to category mapping
test_to_category = {}
for category in categories:
    for subcategory in category["subcategories"]:
        test_to_category[subcategory] = category["category"]

# @login_required
# def pathology_report(request):
#     if request.user.is_superuser or request.session.get('user_role') == 'Pathology':
#         start_date_str = request.GET.get('start_date', None)
#         end_date_str = request.GET.get('end_date', None)
#         department_id = request.GET.get('department', None)
#         test_name_id = request.GET.get('test_name', None)

#         if start_date_str:
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
#         else:
#             start_date = None

#         if end_date_str:
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Include records for the entire end day
#         else:
#             end_date = None

#         print("Start Date:", start_date)
#         print("End Date:", end_date)

#         # Retrieve all test names
#         all_test_names = Patient_registration.objects.values_list('test_name', flat=True)
    
#         # Initialize an empty set to store unique test names
#         unique_test_names = set()
        
#         for test_names in all_test_names:
#             if test_names:
#                 # Split the test names by spaces and add to the set
#                 test_name_list = test_names.split()
#                 unique_test_names.update(test_name_list)
        
#         print("Unique test names:", unique_test_names)
        
#         # Initialize a nested dictionary to store counts by date, department, and test name
#         report_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

#         # Filter Test_reports by date range
#         test_reports = Test_report.objects.all()
#         if start_date and end_date:
#             test_reports = test_reports.filter(created_at__range=(start_date, end_date))
#         elif start_date:
#             test_reports = test_reports.filter(created_at__gte=start_date)
#         elif end_date:
#             test_reports = test_reports.filter(created_at__lte=end_date)
        
#         print("Filtered test reports:", test_reports)

#         if start_date_str or end_date_str or department_id or test_name_id:

#             for test_report in test_reports:
#                 report_date = test_report.created_at.strftime('%Y-%m-%d')
#                 report_date_datetime = datetime.strptime(report_date, '%Y-%m-%d')
                
#                 if start_date is None or report_date_datetime >= start_date:
#                     report_department = test_report.patient.department.name if test_report.patient.department else 'Unknown'
#                     test_names = test_report.patient.test_name.split() if test_report.patient.test_name else []
                    
#                     for test_name in test_names:
#                         report_data[report_date][report_department][test_name] += 1
            
            
#             print("Report data:")
#             for date, departments in report_data.items():
#                 for department, tests in departments.items():
#                     for test, count in tests.items():
#                         print(f"Date: {date}, Department: {department}, Test: {test}, Count: {count}")
                    
#             prepared_report_data = []
#             for date, departments in report_data.items():
#                 for department, tests in departments.items():
#                     for test, count in tests.items():
#                         category = test_to_category.get(test, "Unknown")
#                         prepared_report_data.append({
#                             'date': date,
#                             'department': department,
#                             'test_name': test,
#                             'count': count,
#                             'category': category
#                         })
            
#             print("Prepared report data:", prepared_report_data)
#             prepared_report_data.sort(key=lambda x: (x['date'], x['department'], x['category']))
#         else:
#             prepared_report_data = {}
#         pd = PathologyDepartment.objects.all().order_by('name')
#         return render(request, 'pathology_report.html', {'report_data': prepared_report_data, 'title': 'Pathology Report', 'unique_test_names':unique_test_names, 'departments' : pd})
#     else:
#         logout(request)
#         return redirect('signin')



@login_required
def pathology_report(request):
    if request.user.is_superuser or request.session.get('user_role') == 'Pathology':
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        department_id = request.GET.get('department', None)
        test_name_id = request.GET.get('test_name', None)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Include records for the entire end day
        else:
            end_date = None

        print("Start Date:", start_date)
        print("End Date:", end_date)

        # Retrieve all test names
        all_test_names = Patient_registration.objects.values_list('test_name', flat=True)
    
        # Initialize an empty set to store unique test names
        unique_test_names = set()
        
        for test_names in all_test_names:
            if test_names:
                # Split the test names by spaces and add to the set
                test_name_list = test_names.lower().split()
                unique_test_names.update(test_name_list)
        
        print("Unique test names:", unique_test_names)
        
        # Initialize a nested dictionary to store counts by date, department, and test name
        report_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        # Filter Test_reports by date range
        test_reports = Test_report.objects.all()
        if start_date and end_date:
            test_reports = test_reports.filter(created_at__range=(start_date, end_date))
        elif start_date:
            test_reports = test_reports.filter(created_at__gte=start_date)
        elif end_date:
            test_reports = test_reports.filter(created_at__lte=end_date)

        if department_id and department_id != 'All':
            test_reports = test_reports.filter(patient__department__department_id=department_id)
        
        if test_name_id and test_name_id != 'All':
            test_reports = test_reports.filter(patient__test_name__icontains=test_name_id)

        print("Filtered test reports:", test_reports)
        total = 0
        if start_date_str or end_date_str or department_id or test_name_id:

            for test_report in test_reports:
                report_date = test_report.created_at.strftime('%Y-%m-%d')
                report_date_datetime = datetime.strptime(report_date, '%Y-%m-%d')
                
                if start_date is None or report_date_datetime >= start_date:
                    report_department = test_report.patient.department.name if test_report.patient.department else 'Unknown'
                    
                    test_names = test_report.patient.test_name.lower().split() if test_report.patient.test_name else []
                    
                    for test_name in test_names:
                        if test_name_id and test_name_id != 'All':
                            if test_name_id == test_name:
                                report_data[report_date][report_department][test_name] += 1
                                total += 1
                        else:
                            report_data[report_date][report_department][test_name] += 1
                            total += 1
            
            print("Report data:")
            for date, departments in report_data.items():
                for department, tests in departments.items():
                    for test, count in tests.items():
                        print(f"Date: {date}, Department: {department}, Test: {test}, Count: {count}")
                    
            prepared_report_data = []
            for date, departments in report_data.items():
                for department, tests in departments.items():
                    for test, count in tests.items():
                        category = test_to_category.get(test, "Unknown")
                        prepared_report_data.append({
                            'date': date,
                            'department': department,
                            'test_name': test,
                            'count': count,
                            'category': category
                        })
            
            print("Prepared report data:", prepared_report_data)
            prepared_report_data.sort(key=lambda x: (x['date'], x['department'], x['category']))
        else:
            prepared_report_data = {}
        pd = PathologyDepartment.objects.all().order_by('name')
        return render(request, 'pathology_report.html', {'report_data': prepared_report_data, 'title': 'Pathology Report', 'unique_test_names':unique_test_names, 'departments' : pd, 'total' : total, 'start_date_str' : start_date_str, 'end_date_str' : end_date_str})
    else:
        logout(request)
        return redirect('signin')


@login_required
def pathology_report_location_wise(request):
    if request.user.is_superuser or request.session.get('user_role') == 'Pathology':
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department', None)
        category_id = request.GET.get('category', None)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Include records for the entire end day
        else:
            end_date = None

        print("Start Date:", start_date)
        print("End Date:", end_date)

        all_test_names = Patient_registration.objects.values_list('test_name', flat=True)
    
        # Initialize an empty set to store unique test names
        unique_test_names = set()
        
        for test_names in all_test_names:
            if test_names:
                # Split the test names by spaces and add to the set
                test_name_list = test_names.lower().split()
                unique_test_names.update(test_name_list)
        
        print("Unique test names:", unique_test_names)
        
        # Initialize a nested dictionary to store counts by date, department, and category
        report_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        # Filter Test_reports by date range
        test_reports = Test_report.objects.all()
        if start_date and end_date:
            test_reports = test_reports.filter(created_at__range=(start_date, end_date))
        elif start_date:
            test_reports = test_reports.filter(created_at__gte=start_date)
        elif end_date:
            test_reports = test_reports.filter(created_at__lte=end_date)
        
        if department_id and department_id != 'All':
            test_reports = test_reports.filter(patient__department__department_id=department_id)
        
        # Define the categories and subcategories
        categories = [
            {
                "category": "Immuno Assay (Thyroid)",
                "subcategories": [
                    "TSH", "T3", "T4", "FT3", "FT4", "LH", "FSH",
                    "Prolectin", "CA-125", "PSA", "Anti CCP",
                    "Vitamin B12", "Vitamin D3", "AMH"
                ]
            },
            {
                "category": "Hematology",
                "subcategories": ["CBC", "HbA1c", "ESR", "BT", "CT", "MP"]
            },
            {
                "category": "Serology",
                "subcategories": [
                    "HIV", "HBSAg", "HCV", "Widal", "Malaria",
                    "Dengue Test", "Typhoid Test", "VDRL", "RPR"
                ]
            },
            {
                "category": "Cytopathology",
                "subcategories": ["PAP Smear", "FNAC", "CSF", "Pleural Fluid", "Ascitic Fluid"]
            },
            {
                "category": "Histopathology",
                "subcategories": ["Biopsy"]
            },
            {
                "category": "Bio-Chemistry",
                "subcategories": [
                    "Sugar", "B. Urea", "S. Creatinine", "S. Uric Acid",
                    "D. Bilirubin", "T. Bilirubin", "SGPT (ALT)",
                    "SGOT (AST)", "T. Protein", "Albumin", "ALP", "GGT",
                    "Cholesterol", "TGL", "HDL", "LDL", "VLDL", "CRP",
                    "ASO", "RA Factor", "Amylase", "Lipase", "HbA1c",
                    "Calcium", "S. Electrolytes", "Ferritin", "Acid Phosphatase",
                    "Iron", "TIBC (Total Iron Binding Capacity)",
                    "Magnesium", "Phosphorous", "CPK", "CK-MB", "CK-NAC", "LFT", "KFT", "TLP"
                ]
            }
        ]

        # Create a dictionary mapping test names to categories
        test_to_category = {}
        for category in categories:
            for subcategory in category["subcategories"]:
                test_to_category[subcategory.lower()] = category["category"].lower()

        print("Filtered test reports:", test_reports)
        total = 0
        if start_date_str or end_date_str or department_id or category_id:
            # Normalize category_id to lowercase
            category_id = category_id.lower() if category_id else None

            # Aggregate counts
            for test_report in test_reports:
                report_date = test_report.created_at.strftime('%Y-%m-%d')
                report_date_datetime = datetime.strptime(report_date, '%Y-%m-%d')
                
                if start_date is None or report_date_datetime >= start_date:
                    report_department = test_report.patient.department.name if test_report.patient.department else ''
                    test_names = test_report.patient.test_name.lower().split() if test_report.patient.test_name else []

                    # Track if any test name in the report matches the category
                    category_matched = False
                    for test_name in test_names:
                        category = test_to_category.get(test_name, "unknown")
                        if category_id and category_id != 'all':
                            if category_id == category:
                                category_matched = True
                        else:
                            report_data[report_date][report_department][category] += 1
                            total += 1
                    
                    if category_matched:
                        report_data[report_date][report_department][category_id] += 1
                        total += 1

            print("Report data:")
            for date, departments in report_data.items():
                for department, categories in departments.items():
                    for category, count in categories.items():
                        print(f"Date: {date}, Department: {department}, Category: {category}, Count: {count}")
            
            prepared_report_data = []
            for date, departments in report_data.items():
                for department, categories in departments.items():
                    for category, count in categories.items():
                        prepared_report_data.append({
                            'date': date,
                            'department': department,
                            'category': category,
                            'count': count
                        })
            
            print("Prepared report data:", prepared_report_data)
            prepared_report_data.sort(key=lambda x: (x['date'], x['department'], x['category']))
        else:
            prepared_report_data = {}
        pd = PathologyDepartment.objects.all().order_by('name')
        
        return render(request, 'pathology_report_location.html', {'report_data': prepared_report_data, 'title': 'Pathology Report', 'departments' : pd, 'total' : int(total), 'start_date_str' : start_date_str, 'end_date_str' : end_date_str})
    else:
        logout(request)
        return redirect('signin')
