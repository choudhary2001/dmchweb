from django.shortcuts import render, redirect
from .models import *
from drug.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Min, Max
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
import pytz
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlparse, parse_qs, unquote_plus
from django.db.models import Q
import csv
from django.http import HttpResponse
from collections import OrderedDict
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MedicineConsumption, DrugDepartment
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum

@login_required
def supply_details_view(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name=departpment).first()

    if request.user.is_superuser or d is not None:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name', None)

        # Parsing dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

        p = Supply.objects.filter(departpment=d).order_by('-order_date')
        all_medicines = MedicineConsumption.objects.filter(departpment=d).all()

        if start_date and end_date:
            p = p.filter(order_date__range=(start_date, end_date))
            all_medicines = all_medicines.filter(created_at__range=(start_date, end_date))
        elif start_date:
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
            all_medicines = all_medicines.filter(created_at__range=(start_datetime, end_datetime))
        elif end_date:
            p = p.filter(order_date__lt=end_date)
            all_medicines = all_medicines.filter(created_at__lt=end_date)

        department = None
        if product_name and product_name != 'All':
            ps = ProductSupply.objects.filter(productdetails_id=product_name).first()
            if ps:
                p = p.filter(products=ps)
                department = ps.productdetails_id

        product_quantities = {}
        for supply in p:
            products = supply.products.all()
            for product in products:
                product_id = product.productdetails_id
                total_consumption = all_medicines.filter(products__product__productdetails_id=product_id).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                if product_id not in product_quantities:
                    product_quantities[product_id] = {
                        'product_name': product.product_name,
                        'product_type': product.product_type,
                        'mfg_name': product.mfg_name,
                        'mfg_date': product.mfg_date,
                        'exp_date': product.exp_date,
                        'batch_no': product.batch_no,
                        'quantity': product.quantity,
                        'stock_quantity': product.stock_quantity,
                        'total_consumption': total_consumption,
                        'remaining_quantity': product.quantity - total_consumption,
                        'remarks': product.remarks,
                        'supply_date': supply.order_date,
                        'created_at': product.created_at
                    }
                    if product.stock_quantity != product.quantity - total_consumption:
                        product.stock_quantity = product.quantity - total_consumption
                        product.save()
                else:
                    product_quantities[product_id]['quantity'] += product.quantity

        # Sort the product_quantities dictionary by product_name
        product_quantities = OrderedDict(sorted(product_quantities.items(), key=lambda x: x[1]['product_name'].lower()))

        de = DrugDepartment.objects.all()
        unique_p_types = [
            {'productdetails_id': ps.productdetails_id, 'product_name': ps.product_name}
            for s in Supply.objects.filter(departpment=d)
            for ps in s.products.all()
        ]

        # Get all consumption details
        consumptions = MedicineConsumption.objects.filter(departpment=d).select_related('patient')

        context = {
            'supply': p,
            'title': f"Stock: {len(p)}",
            'departments': de,
            'department': department,
            'productsupply': unique_p_types,
            'consumptions': consumptions,
            'product_quantities': product_quantities
        }

        return render(request, 'medicine_store/stock.html', context=context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def supply_details_view_data(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name=departpment).first()

    if request.user.is_superuser or d is not None:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name', None)

        # Parsing dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

        p = Supply.objects.filter(departpment=d).order_by('-order_date')
        all_medicines = MedicineConsumption.objects.filter(departpment=d).all()

        if start_date and end_date:
            p = p.filter(order_date__range=(start_date, end_date))
            all_medicines = all_medicines.filter(created_at__range=(start_date, end_date))
        elif start_date:
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
            all_medicines = all_medicines.filter(created_at__range=(start_datetime, end_datetime))
        elif end_date:
            p = p.filter(order_date__lt=end_date)
            all_medicines = all_medicines.filter(created_at__lt=end_date)

        department = None
        if product_name and product_name != 'All':
            ps = ProductSupply.objects.filter(productdetails_id=product_name).first()
            if ps:
                p = p.filter(products=ps)
                department = ps.productdetails_id

        product_quantities = {}
        for supply in p:
            products = supply.products.all()
            for product in products:
                product_id = product.productdetails_id
                total_consumption = all_medicines.filter(products__product__productdetails_id=product_id).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                if product_id not in product_quantities:
                    product_quantities[product_id] = {
                        'product_name': product.product_name,
                        'product_type': product.product_type,
                        'mfg_name': product.mfg_name,
                        'mfg_date': product.mfg_date,
                        'exp_date': product.exp_date,
                        'batch_no': product.batch_no,
                        'quantity': product.quantity,
                        'stock_quantity': product.stock_quantity,
                        'total_consumption': total_consumption,
                        'remaining_quantity': product.quantity - total_consumption,
                        'remarks': product.remarks,
                        'supply_date': supply.order_date,
                        'created_at': product.created_at
                    }
                    if product.stock_quantity != product.quantity - total_consumption:
                        product.stock_quantity = product.quantity - total_consumption
                        product.save()
                else:
                    product_quantities[product_id]['quantity'] += product.quantity

        # Sort the product_quantities dictionary by product_name
        product_quantities = OrderedDict(sorted(product_quantities.items(), key=lambda x: x[1]['product_name'].lower()))

        de = DrugDepartment.objects.all()
        unique_p_types = [
            {'productdetails_id': ps.productdetails_id, 'product_name': ps.product_name}
            for s in Supply.objects.filter(departpment=d)
            for ps in s.products.all()
        ]

        # Get all consumption details
        consumptions = MedicineConsumption.objects.filter(departpment=d).select_related('patient')

        context = {
            'supply': p,
            'title': f"Stock: {len(p)}",
            'departments': de,
            'department': department,
            'productsupply': unique_p_types,
            'consumptions': consumptions,
            'product_quantities': product_quantities
        }

        return render(request, 'medicine_store/stockreport.html', context=context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def supply_details_view_print(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range
        p = Supply.objects.filter(departpment=d).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_date, order_date__lt=end_datetime)
        elif end_date:
            p = p.filter(order_date__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = DrugDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    p = p.filter(departpment = de)
                    print(p)
                    department = de.name


        d = DrugDepartment.objects.all()
        sp = ProductSupply.objects.all().order_by('-created_at')
        # sp = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()
        unique_p_types = []
        ss = Supply.objects.all()
        print(ss)
        for s in ss:
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        print(unique_p_types)
        context = {
            'supply' : p,
            'title' : f"Stock : {len(p)}",
            'departments' : d,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/stockprint.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def receivedsupply_details_view(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
    # if True:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date')
        product_name = request.GET.get('product_name')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')   # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        p = Supply.objects.filter(departpment=d, de = None).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_date, order_date__lt=end_datetime)
        elif end_date:
            p = p.filter(order_date__lt=end_date)

        department = None
        if product_name != None:
            if product_name != 'All':
                ps = ProductSupply.objects.filter(productdetails_id = product_name).first()
                print(ps)
                if ps:
                    p = p.filter(products = ps)
                    print(p)
                    department = ps.productdetails_id


        d = DrugDepartment.objects.all()
        # unique_p_types = ProductSupply.objects.all().order_by('-created_at')
        # unique_p_types = ProductSupply.objects.values_list('product_name', flat=True).distinct()
        # unique_products = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()
        unique_p_types = []
        ss = Supply.objects.all()
        print(ss)
        for s in ss:
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name,'mfg_name' : ps.mfg_name, 'batch_no' : ps.batch_no, 'mfg_date' : ps.mfg_date, 'exp_date'  : ps.exp_date, 'stock_quantity' : ps.stock_quantity  })
        print(unique_p_types)
        context = {
            'supply' : p,
            'title' : f"Received Stock : {len(p)}",
            'departments' : d,
            'department' : department,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/rstock.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def receivedsupply_details_print(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
    # if True:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date')
        product_name = request.GET.get('product_name')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        p = Supply.objects.filter(departpment=d, de = None).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_date, order_date__lt=end_datetime)
        elif end_date:
            p = p.filter(order_date__lt=end_date)

        department = None
        if product_name != None:
            if product_name != 'All':
                ps = ProductSupply.objects.filter(productdetails_id = product_name).first()
                print(ps)
                if ps:
                    p = p.filter(products = ps)
                    print(p)
                    department = ps.productdetails_id


        d = DrugDepartment.objects.all()
        # unique_p_types = ProductSupply.objects.all().order_by('-created_at')
        # unique_p_types = ProductSupply.objects.values_list('product_name', flat=True).distinct()
        # unique_products = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()
        unique_p_types = []
        ss = Supply.objects.all()
        print(ss)
        for s in ss:
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        print(unique_p_types)
        context = {
            'supply' : p,
            'title' : f"Received Stock : {len(p)}",
            'departments' : d,
            'department' : department,
            'productsupply' : unique_p_types,
            'start_date_str' : start_date_str,
            'end_date_str' : end_date_str

        }
        return render(request, 'medicine_store/rstockprint.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def get_medicine_names_by_type(request):
    department = request.session['user_role']
    d = DrugDepartment.objects.filter(name=department).first()
    
    if request.user.is_superuser or request.session['user_role'] == 'Drug' or request.session['user_role_store'] == 'Medicine Store':
        product_type = request.GET.get('product_type')
        product_names = []

        unique_p_types = []
        ss = Supply.objects.all()
        
        for s in ss:
            if s.departpment.name == department:
                sp = s.products.all()
                for ps in sp:
                    if ps.stock_quantity > 0:
                        if product_type == ps.product_type:
                            if ps.exp_date:
                                if ps.exp_date <= timezone.now().date() + timedelta(days=3*30):
                                    expire = True
                                else:
                                    expire = False
                            else:
                                expire = False
                            if s.order_date:
                                # order_date = s.order_date.strftime("%d-%m-%Y")
                                order_date = s.order_date + timedelta(days=1)
                                order_date = order_date.strftime("%d-%m-%Y")
                            else:
                                order_date = 'N/A'
                            unique_p_types.append({
                                'productdetails_id': ps.productdetails_id,
                                'product_name': ps.product_name,
                                'mfg_name': ps.mfg_name,
                                'batch_no': ps.batch_no,
                                'mfg_date': ps.mfg_date,
                                'exp_date': ps.exp_date,
                                'stock_quantity': ps.stock_quantity,
                                'order_date': order_date,
                                'expire' : expire
                            })

        # Sort the unique_p_types list alphabetically by product_name
        unique_p_types = sorted(unique_p_types, key=lambda x: x['product_name'])

        return JsonResponse({'products': unique_p_types})
    else:
        logout(request)
        return redirect('signin')

@login_required
def medicine_supply_add_view(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        current_time_utc = timezone.now()
        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        current_date = current_time_kolkata.date()

        if departpment == 'OPD Med Store':
            request.session['supply_date'] = current_date.strftime('%Y-%m-%d')

        aps = Supply.objects.filter(departpment=d).order_by('-order_date')
        all_medicines = MedicineConsumption.objects.filter(departpment=d).all()


        product_quantities = {}
        for supply in aps:
            products = supply.products.all()
            for product in products:
                product_id = product.productdetails_id
                total_consumption = all_medicines.filter(products__product__productdetails_id=product_id).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                if product_id not in product_quantities:
                    product_quantities[product_id] = {
                        'product_name': product.product_name,
                        'product_type': product.product_type,
                        'mfg_name': product.mfg_name,
                        'mfg_date': product.mfg_date,
                        'exp_date': product.exp_date,
                        'batch_no': product.batch_no,
                        'quantity': product.quantity,
                        'stock_quantity': product.stock_quantity,
                        'total_consumption': total_consumption,
                        'remaining_quantity': product.quantity - total_consumption,
                        'remarks': product.remarks,
                        'supply_date': supply.order_date,
                        'created_at': product.created_at
                    }
                    if product.stock_quantity != product.quantity - total_consumption:
                        product.stock_quantity = product.quantity - total_consumption
                        product.save()
                else:
                    product_quantities[product_id]['quantity'] += product.quantity

            
        if request.method == 'POST':
            # Get the current time in UTC


                
            # Extract data from the form
            print(request.POST)
            regid = request.POST.get('regid', None)
            patient_name = request.POST.get('patient_name', None)
            supply_date = request.POST.get(f'supply_date')

            request.session['supply_date'] = supply_date

            # p = Patient.objects.filter(regid=regid).first()
            try:
                p = Patient.objects.filter(regid = regid).first()
            except Exception as e:
                # print(e)
                try:
                    p = Patient.objects.filter(regnoid = regid).first()
                except Exception as e:
                    # print(e)
                    p = None
            # try:
            #     duplicate_patient = MedicineConsumption.objects.filter(
            #         user = request.user,
            #         patient=p,
            #         patient_name = patient_name, 
            #         regno = regid,
            #         departpment = d,
            #         created_at = current_time_kolkata
            #     ).first()
            #     if duplicate_patient:
            #         messages.error(request, 'Duplicate patient found. Please check the details and try again.')
            #         return redirect(f"/medicine_store/supply/medicine/")
            # except Exception as e:
            #     print(e)

            # Create a new supply instance
            m = MedicineConsumption.objects.create(
                user = request.user,
                patient=p,
                patient_name = patient_name, 
                regno = regid,
                departpment = d
            )


            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                

                ps = ProductSupply.objects.filter(productdetails_id = product_name).first()
                print(ps)
                if ps:
                    if int(ps.stock_quantity) >= int(quantity) :
                        ps.stock_quantity = int(ps.stock_quantity) -  int(quantity)
                        ps.save()
                        product = Medicine.objects.create(
                            product = ps,
                            quantity=quantity,
                            created_at = supply_date,
                            departpment = d
                        )
                        
                        m.products.add(product)
                    
            # Save the order
            m.save()
            messages.success(request, 'Added Successfully')

            return redirect(f"/medicine_store/supply/medicine/")

        s = Suppliar.objects.all().order_by('-created_at')
        dd = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        sp = ProductSupply.objects.all().order_by('-created_at')

        # unique_p_typess = ProductType.objects.values_list('p_type', flat=True).distinct().order_by('p_type')
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True)
        # ss = Supply.objects.filter(departpment=d).order_by('-order_date')
        # unique_p_types = ss.products.all()
        
        unique_p_typess = set()
        all_supply = Supply.objects.filter(departpment = d).all()
        for a in all_supply:
            ap = a.products.all()
            for p in ap:
                if p.product:
                    unique_p_typess.add(
                        p.product.p_type
                    )
        unique_p_typess = sorted(unique_p_typess)
        print(unique_p_typess)

        unique_p_types = []
        ss = Supply.objects.all()
        # print(ss)
        for s in ss:
            print(s.departpment, dd)
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    if ps.stock_quantity > 0:
                        # unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
                        unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name,'mfg_name' : ps.mfg_name, 'batch_no' : ps.batch_no, 'mfg_date' : ps.mfg_date, 'exp_date'  : ps.exp_date, 'stock_quantity' : ps.stock_quantity, 'order_date' : ps.order_date  })


        # print(unique_p_types)
        suppliesss = Supply.objects.filter(departpment=d).order_by('-order_date')
        # print(suppliesss)
        # Initialize an empty list to store the expiring products
        expiring_productss = []

        # Loop through each supply
        for supplys in suppliesss:
            # Get the related ProductSupply instances for the current supply
            product_supplies = supplys.products.all()
            # print(product_supplies)
            # Loop through each product supply
            for product_supplyy in product_supplies:
                # print(product_supplyy)
                # Check if the exp_date is less than 3 months from today
                if product_supplyy.exp_date is not None and product_supplyy.exp_date <= timezone.now().date() + timedelta(days=3*30) and product_supplyy.stock_quantity > 0:
                    # If it is, add relevant details to the expiring_products list
                    # print('###')
                    expiring_productss.append({
                        'product_type': product_supplyy.product_type,
                        'product_name': product_supplyy.product_name,
                        'mfg_name': product_supplyy.mfg_name,
                        'mfg_date': product_supplyy.mfg_date,
                        'exp_date': product_supplyy.exp_date,
                        'batch_no': product_supplyy.batch_no,
                        'stock_quantity': product_supplyy.stock_quantity,
                        'supply_date': product_supplyy.supply_date,
                    })

        context = {
            'title' : 'Medicine Consumption / Supply',
            'suppliar' : s,
            'department' : dd,
            'product' : p,
            'unique_p_types' : unique_p_typess,
            'productsupply' : unique_p_types,
            'expiring_products' : expiring_productss,
            

        }
        return render(request, 'medicine_store/supply.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def medicine_supply_update_view(request, consumption_id):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        m = MedicineConsumption.objects.filter(consumption_id = consumption_id).first()

        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            regid = request.POST.get('regid', None)
            patient_name = request.POST.get('patient_name', None)
            supplyy_date = request.POST.get(f'supplyy_date')
            # p = Patient.objects.filter(regid=regid).first()
            try:
                p = Patient.objects.filter(regid = regid).first()
            except Exception as e:
                print(e)
                try:
                    p = Patient.objects.filter(regnoid = regid).first()
                except Exception as e:
                    print(e)
                    p = None
            try:
                if request.session['user_role'] == 'Emergency Med Store':
                    if p:
                        supply.patient = p
                    if regid:
                        supply.regno = regid
                    if patient_name:
                        supply.patient_name = patient_name
            except Exception as e:
                print(e)

            request.session['supply_date'] = supplyy_date



            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                medicine_id = request.POST.get(f'medicine_id_{i}')
                productdetails_id = request.POST.get(f'productdetails_id_{i}')

                ps = ProductSupply.objects.filter(productdetails_id = product_name).first()
                print(ps)
                med = Medicine.objects.filter(medicine_id = medicine_id).first()
                print(med)
                if med and ps:
                    print(quantity)
                    if med.product.productdetails_id == ps.productdetails_id:
                        med.created_at = supplyy_date
                        if int(med.product.stock_quantity) >= int(quantity):
                            quantity_m = int(med.product.stock_quantity) +  int(med.quantity) - int(quantity)
                            med.product.stock_quantity = quantity_m
                            med.product.save()
                            med.quantity = quantity
                        med.save()
                    else:
                        med.product.stock_quantity = int(med.product.stock_quantity) +  int(med.quantity)
                        med.product.save()
                        med.created_at = supplyy_date
                        if int(ps.stock_quantity) >= int(quantity):
                            ps.stock_quantity = int(ps.stock_quantity) -  int(quantity)
                            ps.save()
                            med.product = ps
                            med.quantity = quantity
                        med.save()
                else:
                    if ps:
                        if int(ps.stock_quantity) >= int(quantity) :
                            ps.stock_quantity = int(ps.stock_quantity) -  int(quantity)
                            ps.save()
                            product = Medicine.objects.create(
                                product = ps,
                                quantity=quantity,
                                created_at = supplyy_date
                            )
                            
                            m.products.add(product)   
            m.save()
            messages.success(request, 'Updated Successfully')
            return redirect(f'/medicine_store/supply/medicine/{consumption_id}/update/')

        s = Suppliar.objects.all().order_by('-created_at')
        dee = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        sp = ProductSupply.objects.all().order_by('-created_at')
        medicine = get_object_or_404(MedicineConsumption, consumption_id=consumption_id)
        # unique_p_typess = ProductType.objects.values_list('p_type', flat=True).distinct().order_by('p_type')

        # unique_p_typess = ProductSupply.objects.values_list('product_type', flat=True).distinct().order_by('product_type')
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True)
        # ss = Supply.objects.filter(departpment=d).order_by('-order_date')
        # unique_p_types = ss.products.all()

        
        unique_p_typess = set()
        all_supply = Supply.objects.filter(departpment = d).all()
        for a in all_supply:
            ap = a.products.all()
            for p in ap:
                if p.product:
                    unique_p_typess.add(
                        p.product.p_type
                    )
        unique_p_typess = sorted(unique_p_typess)
        # print(unique_p_typess)


        unique_p_types = []
        ss = Supply.objects.all()
        # print(ss)
        for s in ss:
            # print(s.departpment, d)
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    if ps.stock_quantity > 0:
                        unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        # print(unique_p_types)
        
        first_medicine_date = None
        first_medicine = m.products.order_by('created_at').first()
        # print(first_medicine)
        if first_medicine:
            first_medicine_date = first_medicine.created_at
        # print(first_medicine_date)

        context = {
            'title' : 'Medicine Consumption / Supply',
            'suppliar' : s,
            'department' : dee,
            'product' : p,
            'unique_p_types' : unique_p_typess,
            'productsupply' : unique_p_types,
            'medicine' : medicine,
            'total' : len(medicine.products.all()),
            'first_medicine_date': first_medicine_date,
        }
        return render(request, 'medicine_store/supply_update.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def medicine_supply_delete_view(request, consumption_id):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        m = MedicineConsumption.objects.filter(consumption_id = consumption_id).first()
        if m is not None:
            mm = m.products.all()
            for mp in mm:
                mp.product.stock_quantity += mp.quantity
                mp.product.save()

            m.delete()
            messages.success(request, 'Deleted Successfully')

        return redirect('supply_details_user_view') 

    else:
        logout(request)
        return redirect('signin') 

@login_required
def medicine_supply_product_delete_view(request, medicine_id):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        m = Medicine.objects.filter(medicine_id = medicine_id).first()
        print(m)
        if m is not None:
            m.product.stock_quantity += m.quantity
            m.product.save()
            m.delete()
            messages.success(request, 'Deleted Successfully')

        return redirect('supply_details_user_view') 

    else:
        logout(request)
        return redirect('signin') 

@login_required
def get_medicine_details(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    print(departpment, d)
    # Get the selected product type from the AJAX request
    product_name = request.GET.get('product_name')
    print(product_name)
    if product_name:
        # Retrieve the ProductPurchase object
        s = Supply.objects.filter(departpment = d).all()
        product_supply = ProductSupply.objects.filter(productdetails_id=product_name).first()
        print(product_supply)
        # Check if the ProductPurchase object exists
        if product_supply:
            # Convert the model instance to a dictionary
            product_purchase_dict = model_to_dict(product_supply)
            # Return the dictionary as JSON response
            return JsonResponse({'product': product_purchase_dict})
    else:
        # If no product purchase found, return empty response or appropriate error message
        return JsonResponse({'error': 'Product purchase not found for the given product name'}, status=404)

@login_required
def supply_details_user_view(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')

        if start_date_str:
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') 
        else:
            end_date = None
        # pr = Profile.objects.filter(user_role = departpment).all()

        # p = MedicineConsumption.objects.filter(user = request.user).order_by('-created_at')
        # Get all profiles with the specified user role
        # profiles = Profile.objects.filter(user_role=departpment).select_related('user')

        # Extract user IDs from profiles
        # user_ids = [profile.user_id for profile in profiles]

        # Filter MedicineConsumption objects for the users with the specified user role
        # p = MedicineConsumption.objects.filter(user_id__in=user_ids).order_by('-created_at')
        p = MedicineConsumption.objects.filter(departpment= d).order_by('-created_at')


        if start_date and end_date:
            p = p.filter(products__created_at__range=(start_date, end_date))
        elif start_date:
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(products__created_at__gte=start_datetime, products__created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(products__created_at__lt=end_date)

        d = DrugDepartment.objects.all()
        # sp = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()
        # sp = ProductSupply.objects.all().order_by('-created_at')
        unique_p_types = []
        ss = Supply.objects.all()
        print(ss)
        for s in ss:
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        print(unique_p_types)
        
        context = {
            'supply' : p,
            'title' : f"Total Medicine Consumption",
            'departments' : d,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/supplydetails.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_details_user_view_data(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name=departpment).first()
    if request.user.is_superuser or d is not None:
        # Get the current time in UTC
        current_time_utc = timezone.now()
        # request.session['user_role'] = 'Registration'

        # Get the Kolkata timezone
        kolkata_timezone = pytz.timezone('Asia/Kolkata')

        # Convert the current time to Kolkata timezone
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        draw = request.GET.get('draw')
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_query = request.GET.get('searchValue')
        search_p_query = request.GET.get('searchpValue')
        print(search_query)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') 
        else:
            end_date = None

        p = MedicineConsumption.objects.filter(departpment=d).order_by('-created_at')

        if start_date and end_date:
            p = p.filter(products__created_at__range=(start_date, end_date))
        elif start_date:
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(products__created_at__gte=start_datetime, products__created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(products__created_at__lt=end_date)

        # for a in MedicineConsumption.objects.all():
        #     for b in a.products.all():
        #         print(b, a.departpment)
        #         b.departpment = a.departpment
        #         b.save()

        url = search_query
        parsed_url = urlparse(url)
        query_string = parsed_url.query
        query_params = parse_qs(query_string)
        search_value_encoded = query_params.get('search', [''])[0]
        search_value_decoded = unquote_plus(search_value_encoded)

        print("Decoded search value:", search_query)

        if search_query:
            p = p.filter(
                Q(regno__istartswith=search_query) |
                Q(patient_name__istartswith=search_query) |
                Q(patient__name__istartswith=search_query) |
                Q(products__product__product_name__istartswith=search_query) |
                Q(products__product__mfg_name__istartswith=search_query)
            ).distinct()

        if search_p_query:
            p = p.filter(
                Q(regno__istartswith=search_p_query) |
                Q(patient_name__istartswith=search_p_query) |
                Q(patient__name__istartswith=search_p_query) |
                Q(products__product__product_name__istartswith=search_p_query) |
                Q(products__product__mfg_name__istartswith=search_p_query)
            ).distinct()

        paginator = Paginator(p, length)
        page = start // length + 1

        try:
            paginated_data = paginator.page(page)
        except PageNotAnInteger:
            paginated_data = paginator.page(1)
        except EmptyPage:
            paginated_data = paginator.page(paginator.num_pages)


        data = []
        for order in paginated_data:
            for product in order.products.all():
                created_date = product.created_at.strftime("%d-%m-%Y") 
                end_dateee = datetime.strptime(created_date, '%d-%m-%Y') + timedelta(days=1)  # Add one day to include end_date
                if search_query:
                    if product.product:
                        if product.product.product_name.lower().startswith(search_query.lower()) and product.product:
                            data.append({
                                "reg_no": order.regno if order.regno else order.patient.regnoid if order.patient else '',
                                "patient": order.patient_name if order.patient_name else order.patient.name if order.patient else order.regno,
                                "medicine_name": product.product.product_name if product.product else 'None',
                                "mfg_by": product.product.mfg_name if product.product else 'None',
                                "batch": product.product.batch_no if product.product else 'None',
                                "mfg_date": product.product.mfg_date if product.product else 'None',
                                "exp_date": product.product.exp_date if product.product else 'None',
                                "quantity": product.quantity,
                                "stock_quantity": product.product.stock_quantity,
                                "supply_time": end_dateee.strftime("%d-%m-%Y") ,
                                "created_on": order.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                                "actions": f"""
                                    <a href="/medicine_store/supply/medicine/{order.consumption_id}/update/" class="btn btn-primary btn-icon-split">
                                        <span class="icon text-white-50">
                                            <i class="fas fa-arrow-right"></i>
                                        </span>
                                        <span class="text">Edit</span>
                                    </a>
                                    <a href="/medicine_store/supply/medicine/product/{product.medicine_id}/delete/" class="btn btn-danger btn-icon-split">
                                        <span class="icon text-white-50">
                                            <i class="fas fa-trash"></i>
                                        </span>
                                    </a>
                                """
                            })
                    
                else:
                    data.append({
                        "reg_no": order.regno if order.regno else order.patient.regnoid if order.patient else '',
                        "patient": order.patient_name if order.patient_name else order.patient.name if order.patient else order.regno,
                        "medicine_name": product.product.product_name if product.product else 'None',
                        "mfg_by": product.product.mfg_name if product.product else 'None',
                        "batch": product.product.batch_no if product.product else 'None',
                        "mfg_date": product.product.mfg_date if product.product else 'None',
                        "exp_date": product.product.exp_date if product.product else 'None',
                        "quantity": product.quantity,
                        "stock_quantity": product.product.stock_quantity,
                        "supply_time": end_dateee.strftime("%d-%m-%Y") ,
                        "created_on": order.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                        "actions": f"""
                            <a href="/medicine_store/supply/medicine/{order.consumption_id}/update/" class="btn btn-primary btn-icon-split">
                                <span class="icon text-white-50">
                                    <i class="fas fa-arrow-right"></i>
                                </span>
                                <span class="text">Edit</span>
                            </a>
                            <a href="/medicine_store/supply/medicine/product/{product.medicine_id}/delete/" class="btn btn-danger btn-icon-split">
                                <span class="icon text-white-50">
                                    <i class="fas fa-trash"></i>
                                </span>
                            </a>
                        """
                    })

        print(data)
        return JsonResponse({
            "draw": draw,
            "recordsTotal": paginator.count,
            "recordsFiltered": paginator.count,
            "data": data
        }, safe=False)
    else:
        logout(request)
        return redirect('signin')

@login_required
def supply_details_user_view_print(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')

        if start_date_str:
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') 
        else:
            end_date = None
        # pr = Profile.objects.filter(user_role = departpment).all()

        # p = MedicineConsumption.objects.filter(user = request.user).order_by('-created_at')
        # Get all profiles with the specified user role
        # profiles = Profile.objects.filter(user_role=departpment).select_related('user')

        # Extract user IDs from profiles
        # user_ids = [profile.user_id for profile in profiles]

        # Filter MedicineConsumption objects for the users with the specified user role
        # p = MedicineConsumption.objects.filter(user_id__in=user_ids).order_by('-created_at')
        p = MedicineConsumption.objects.filter(departpment= d).order_by('-created_at')

        # if start_date and end_date:
        #     p = p.filter(created_at__range=(start_date, end_date))

        # elif start_date:
        #     next_day = start_date + timedelta(days=1)
        #     start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
        #     end_datetime = start_datetime + timedelta(days=1)
        #     p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)

        # elif end_date:
        #     p = p.filter(created_at__lt=end_date)

        if start_date and end_date:
            p = p.filter(products__created_at__range=(start_date, end_date))
        elif start_date:
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(products__created_at__gte=start_datetime, products__created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(products__created_at__lt=end_date)

        d = DrugDepartment.objects.all()
        # sp = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()
        # sp = ProductSupply.objects.all().order_by('-created_at')
        unique_p_types = []
        ss = Supply.objects.all()
        print(ss)
        for s in ss:
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        print(unique_p_types)
        
        context = {
            'supply' : p,
            'title' : f"Total Medicine Consumption",
            'departments' : d,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/supplydetails.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_details_user_view_data_data(request):
    department = request.session['user_role']
    d = DrugDepartment.objects.filter(name=department).first()
    
    if request.user.is_superuser or d is not None:
        current_time_utc = timezone.now()
        kolkata_timezone = pytz.timezone('Asia/Kolkata')
        current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)
        
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        search_query = request.GET.get('searchInput')
        search_p_query = request.GET.get('searchpInput')

        print(search_query, search_p_query)
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = None

        data = []
        p = MedicineConsumption.objects.filter(departpment=d).select_related('patient').prefetch_related('products__product').order_by('-created_at')

        if start_date and end_date:
            p = p.filter(products__created_at__range=(start_date, end_date))
        elif start_date:
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(products__created_at__gte=start_datetime, products__created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(products__created_at__lt=end_date)

        if search_query:
            p = p.filter(
                Q(regno__istartswith=search_query) |
                Q(patient_name__istartswith=search_query) |
                Q(patient__name__istartswith=search_query) |
                Q(products__product__product_name__istartswith=search_query) |
                Q(products__product__mfg_name__istartswith=search_query)
            ).distinct()

        seen_products = set()

        for order in p:
            for product in order.products.all():
                product_key = (order.regno, product.product.product_name if product.product else None)
                if search_query:
                    if product.product:
                        if product.product.product_name.lower().startswith(search_query.lower()):
                            if product_key not in seen_products:
                                seen_products.add(product_key)
                                created_date = product.created_at.strftime("%d-%m-%Y")
                                end_dateee = datetime.strptime(created_date, '%d-%m-%Y') + timedelta(days=1)
                                data.append({
                                    "reg_no": order.regno if order.regno else order.patient.regnoid if order.patient else '',
                                    "patient": order.patient_name if order.patient_name else order.patient.name if order.patient else order.regno,
                                    "medicine_name": product.product.product_name if product.product else 'None',
                                    "mfg_by": product.product.mfg_name if product.product else 'None',
                                    "batch": product.product.batch_no if product.product else 'None',
                                    "mfg_date": product.product.mfg_date if product.product else 'None',
                                    "exp_date": product.product.exp_date if product.product else 'None',
                                    "quantity": product.quantity,
                                    "stock_quantity": product.product.stock_quantity,
                                    "supply_time": end_dateee.strftime("%d-%m-%Y"),
                                    "created_on": order.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                                    "actions": f"""
                                        <a href="/medicine_store/supply/medicine/{order.consumption_id}/update/" class="btn btn-primary btn-icon-split">
                                            <span class="icon text-white-50">
                                                <i class="fas fa-arrow-right"></i>
                                            </span>
                                            <span class="text">Edit</span>
                                        </a>
                                        <a href="/medicine_store/supply/medicine/product/{product.medicine_id}/delete/" class="btn btn-danger btn-icon-split">
                                            <span class="icon text-white-50">
                                                <i class="fas fa-trash"></i>
                                            </span>
                                        </a>
                                    """
                                })
                    
                else:
                    if product_key not in seen_products:
                        seen_products.add(product_key)
                        created_date = product.created_at.strftime("%d-%m-%Y")
                        end_dateee = datetime.strptime(created_date, '%d-%m-%Y') + timedelta(days=1)
                        data.append({
                            "reg_no": order.regno if order.regno else order.patient.regnoid if order.patient else '',
                            "patient": order.patient_name if order.patient_name else order.patient.name if order.patient else order.regno,
                            "medicine_name": product.product.product_name if product.product else 'None',
                            "mfg_by": product.product.mfg_name if product.product else 'None',
                            "batch": product.product.batch_no if product.product else 'None',
                            "mfg_date": product.product.mfg_date if product.product else 'None',
                            "exp_date": product.product.exp_date if product.product else 'None',
                            "quantity": product.quantity,
                            "stock_quantity": product.product.stock_quantity,
                            "supply_time": end_dateee.strftime("%d-%m-%Y"),
                            "created_on": order.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                            "actions": f"""
                                <a href="/medicine_store/supply/medicine/{order.consumption_id}/update/" class="btn btn-primary btn-icon-split">
                                    <span class="icon text-white-50">
                                        <i class="fas fa-arrow-right"></i>
                                    </span>
                                    <span class="text">Edit</span>
                                </a>
                                <a href="/medicine_store/supply/medicine/product/{product.medicine_id}/delete/" class="btn btn-danger btn-icon-split">
                                    <span class="icon text-white-50">
                                        <i class="fas fa-trash"></i>
                                    </span>
                                </a>
                            """
                        })
                
        return JsonResponse({
            "recordsTotal": len(p),
            "recordsFiltered": len(p),
            "data": data
        }, safe=False)
    else:
        logout(request)
        return redirect('signin')

@login_required
def supply_details_user_view_print_data(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    print(departpment, d)
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')

        if start_date_str:
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') 
        else:
            end_date = None
        if start_date_str or end_date_str:
            p = MedicineConsumption.objects.filter(departpment= d).order_by('-created_at')

            if start_date and end_date:
                p = p.filter(products__created_at__range=(start_date, end_date))
            elif start_date:
                next_day = start_date + timedelta(days=1)
                start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
                end_datetime = start_datetime + timedelta(days=1)
                p = p.filter(products__created_at__gte=start_datetime, products__created_at__lt=end_datetime)
            elif end_date:
                p = p.filter(products__created_at__lt=end_date)
        else:
            p = None

        d = DrugDepartment.objects.all()
        unique_p_types = []
        ss = Supply.objects.all()
        # print(ss)
        for s in ss:
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        # print(unique_p_types)
        
        context = {
            'supply' : p,
            'title' : f"Total Medicine Consumption",
            'departments' : d,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/supplydetailsprint.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_update_view(request, supply_id):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        supply = get_object_or_404(Supply, supply_id=supply_id)
        # print(supply)
        if request.method == 'POST':
            print(request.POST)
            # Extract data from the form
            indent = request.POST.get('indent')
            department_id = request.POST.get('department_id')
            product_name = request.POST.get('regid')
            product_type = request.POST.get('patient_name')
            mfg_name = request.POST.get('mfg_name')
            order_date = request.POST.get('order_date')
            batch_no = request.POST.get('batch_no')

            # department = DrugDepartment.objects.filter(department_id=department_id).first()


            # supply.department = department
            # supply.indent = indent
            supply.order_date = order_date
            

            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_type_name = request.POST.get(f'product_type_{i}')
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                mrp = request.POST.get(f'mrp_{i}')
                purchaserate = request.POST.get(f'purchaserate_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                stock_quantity = request.POST.get(f'stock_quantity_{i}')
                amount = request.POST.get(f'amount_{i}')
                date = request.POST.get(f'date_{i}')
                productdetails_id = request.POST.get(f'productdetails_id_{i}')
                # supply.order_date = date
                # supply.save()

                print(f"Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")
                pt = ProductType.objects.filter(product_type_id=product_name).first()

                pp = ProductSupply.objects.filter(productdetails_id = productdetails_id).first()
                if pp:
                    if pt:
                        pp.product = pt
                        pp.product_name = pt.name
                        pp.product_type = pt.p_type
                    pp.mfg_name = mfg_name
                    pp.batch_no = batch_no
                    pp.quantity = quantity
                    if mfgdate:
                        pp.mfg_date = mfgdate
                    if expdate:
                        pp.exp_date = expdate
                    pp.stock_quantity = stock_quantity
                    pp.supply_date = order_date

                    pp.save()

            messages.success(request, 'Updated Successfully')
            supply.save()

            return redirect(f'/medicine_store/supply/{supply_id}/update/')
        supply = get_object_or_404(Supply, supply_id=supply_id)

        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')

        unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct().order_by('p_type')
        # total_quantities = {}
        # medicines = MedicineConsumption.objects.filter(departpment=d).all()
        # for m in medicines:
        #     for medicine in m.products.all():
        #         product_id = medicine.product.productdetails_id
        #         if product_id in total_quantities:
        #             total_quantities[product_id] += medicine.quantity
        #         else:
        #             total_quantities[product_id] = medicine.quantity
        # print(total_quantities)
        context = {
            'title' : 'Update Supply',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types,
            'supply' : supply,
            'total' : len(supply.products.all())
        }
        return render(request, 'medicine_store/stockupdate.html', context=context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def stock_add_view(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            indent = request.POST.get('indent')
            department_id = request.POST.get('department_id')
            product_name = request.POST.get('product_name')
            product_type = request.POST.get('product_type')
            mfg_name = request.POST.get('mfg_name')
            batch_no = request.POST.get('batch_no')
            remarks = request.POST.get('remarks')
            order_date = request.POST.get('order_date')

            # department = DrugDepartment.objects.filter(department_id=department_id).first()

            # Create a new supply instance
            supply = Supply.objects.create(
                user = request.user,
                departpment=d,
                indent  = indent,
                de = departpment,
                remarks = remarks,
                order_date = order_date
            )

            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_type_name = request.POST.get(f'product_type_{i}')
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}', None)
                batch_no = request.POST.get(f'batchno_{i}', None)
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                mrp = request.POST.get(f'mrp_{i}', None)
                purchaserate = request.POST.get(f'purchaserate_{i}', None)
                quantity = request.POST.get(f'quantity_{i}')
                amount = request.POST.get(f'amount_{i}')
                product_type_id_column = request.POST.get(f'product_type_id_column_1{i}')

                print(f"Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")

                pt = ProductType.objects.filter(product_type_id=product_name).first()
                print(pt)
                product = ProductSupply.objects.create(
                    user = request.user,
                    product = pt,
                    product_name=pt.name,
                    product_type=pt.p_type,
                    mfg_name=mfg_name,
                    batch_no=batch_no,
                    quantity=quantity,
                    stock_quantity = quantity,
                    supply_date = order_date,
                    department = d
                    
                )
                print(expdate, mfgdate)
                if mfgdate is not None and mfgdate != '':
                    product.mfg_date = mfgdate
                if expdate is not None and expdate != '':
                    product.exp_date = expdate
                product.save()
                supply.products.add(product)
                request.session['stock_date'] = order_date
            # Save the order
            supply.save()

            messages.success(request, 'Added Successfully')
            return redirect (f'/medicine_store/stock/add/')
        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        # unique_p_types = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()

        # unique_p_types = []
        # ss = Supply.objects.all()
        # print(ss)
        # for s in ss:
        #     if s.departpment.name == departpment:
        #         sp = s.products.all()
        #         for ps in sp:
        #             unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        # print(unique_p_types)
        unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct().order_by('p_type')

        context = {
            'title' : 'Add Stock',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types
        }
        return render(request, 'medicine_store/add_supply.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_delete_view(request, supply_id):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        if departpment == 'MCH& GY MED':
            supply = get_object_or_404(Supply, supply_id=supply_id)
            supply.delete()
        return redirect('medicine_supply_details_view') 
    else:
        logout(request)
        return redirect('signin') 

@login_required
def get_consumption_and_remaining_quantity(request):
    department = request.session.get('user_role')
    d = DrugDepartment.objects.filter(name=department).first()
    # Get the current time in UTC
    current_time_utc = timezone.now()
    # request.session['user_role'] = 'Registration'

    # Get the Kolkata timezone
    kolkata_timezone = pytz.timezone('Asia/Kolkata')

    # Convert the current time to Kolkata timezone
    current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)

    current_date = current_time_kolkata.date()
    today_date = current_date.strftime('%Y-%m-%d')

    if request.user.is_superuser or d is not None:
        start_date_str = request.GET.get('start_date', today_date)
        end_date_str = request.GET.get('end_date', today_date)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = None

        all_supplies = Supply.objects.filter(departpment=d).all()
        all_medicines = MedicineConsumption.objects.filter(departpment=d)

        product_quantities = {}
        if start_date and end_date:
            for supply in all_supplies:
                products = supply.products.all()
                for product in products:
                    product_name = product.product_name
                    if product_name not in product_quantities:
                            product_quantities[product_name] = {
                                'opening': 0,
                                'closing': 0,
                                'remaining_quantity': 0,
                                'purchase': 0
                            }
                    
                    product_quantities[product_name]['purchase'] += product.quantity

            for product_name, quantities in product_quantities.items():
                # Opening Quantity
                total_opening_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_before_start = MedicineConsumption.objects.filter(
                    products__created_at__lt=start_date,
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_ = MedicineConsumption.objects.filter(
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_st_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__stock_quantity'))['total_quantity'] or 0

                total_edited = total_opening_quantity - total_consumed_ - total_st_quantity

                if product_name == 'Diclofenac Sodium 50mg':
                    total_edited += 10
                if product_name == 'Diclofenac Gel Tube 1% w/w 30gm':
                    total_edited += 1
                    
                print(product_name,total_opening_quantity, total_consumed_, total_st_quantity, total_edited)

                opening_quantity = total_opening_quantity - total_edited - total_consumed_before_start

                # Closing Quantity
                total_closing_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_till_end = MedicineConsumption.objects.filter(
                    products__created_at__lt=end_date,
                    products__product__product_name=product_name,
                    departpment=d
                  
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                closing_quantity = opening_quantity - total_consumed_till_end


                total_purchase_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = None,
                    order_date__range=[start_date, end_date],

                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                # Consumption within the date range
                total_consumed_in_range = MedicineConsumption.objects.filter(
                    products__created_at__range=[start_date, end_date],
                    products__product__product_name=product_name,
                    departpment=d
                   
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                
                # Update quantities in the dictionary
                product_quantities[product_name]['purchase1'] = total_purchase_quantity
                product_quantities[product_name]['opening'] = opening_quantity
                product_quantities[product_name]['closing'] = opening_quantity - total_consumed_in_range
                product_quantities[product_name]['remaining_quantity'] = total_consumed_in_range
        # print(product_quantities)
        filtered_product_quantities = {k: v for k, v in product_quantities.items() if v['opening'] > 0}
        context = {
            'product_quantities': filtered_product_quantities,
            'title': f"Total Item Wise Consumption: {len(product_quantities)}",
            'start_date_str': start_date_str,
            'end_date_str': end_date_str
        }
        return render(request, 'medicine_store/itemwiseconsumption.html', context=context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def get_consumption_and_remaining_quantityy(request):
    department = request.session.get('user_role')
    d = DrugDepartment.objects.filter(name=department).first()
    # Get the current time in UTC
    current_time_utc = timezone.now()
    # request.session['user_role'] = 'Registration'

    # Get the Kolkata timezone
    kolkata_timezone = pytz.timezone('Asia/Kolkata')

    # Convert the current time to Kolkata timezone
    current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)

    current_date = current_time_kolkata.date()
    today_date = current_date.strftime('%Y-%m-%d')

    if request.user.is_superuser or d is not None:
        start_date_str = request.GET.get('start_date', today_date)
        end_date_str = request.GET.get('end_date', today_date)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = None

        before_day = end_date - timedelta(days = 1)

        all_supplies = Supply.objects.filter(departpment=d).all()
        all_medicines = MedicineConsumption.objects.filter(departpment=d)

        product_quantities = {}
        if start_date and end_date:
            for supply in all_supplies:
                products = supply.products.all()
                for product in products:
                    product_name = product.product_name
                    if product_name not in product_quantities:
                        product_quantities[product_name] = {
                            'opening': 0,
                            'closing': 0,
                            'remaining_quantity': 0,
                            'purchase': 0
                        }
                    product_quantities[product_name]['purchase'] += product.quantity

            for product_name, quantities in product_quantities.items():
                # Opening Quantity
                total_opening_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_before_start = MedicineConsumption.objects.filter(
                    products__created_at__lte=start_date,
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_ = MedicineConsumption.objects.filter(
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_st_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__stock_quantity'))['total_quantity'] or 0

                total_edited = total_opening_quantity - total_consumed_ - total_st_quantity

                # if product_name == 'Diclofenac Sodium 50mg':
                #     total_edited += 10

                opening_quantity = total_opening_quantity - total_edited - total_consumed_before_start

                # Closing Quantity
                total_closing_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = department,
                    order_date__lt=start_date,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_purchase_quantityy = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = None,
                    order_date__lt=end_date,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_till_end = MedicineConsumption.objects.filter(
                    products__created_at__lt=start_date,
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                
                print(product_name,total_closing_quantity, total_purchase_quantityy, total_consumed_till_end, total_edited)

                closing_quantity = total_closing_quantity + total_purchase_quantityy - total_consumed_till_end - total_edited


                total_purchase_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = None,
                    order_date__range=[start_date, end_date],
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0


                # Consumption within the date range
                total_consumed_in_range = MedicineConsumption.objects.filter(
                    products__created_at__range=[start_date, end_date],
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                # Update quantities in the dictionary
                product_quantities[product_name]['purchase1'] = total_purchase_quantity
                product_quantities[product_name]['opening'] = closing_quantity + total_purchase_quantity
                product_quantities[product_name]['closing'] = closing_quantity + total_purchase_quantity - total_consumed_in_range
                product_quantities[product_name]['remaining_quantity'] = total_consumed_in_range
        # print(product_quantities)
        filtered_product_quantities = {k: v for k, v in product_quantities.items() if v['opening'] != 0}

        context = {
            'product_quantities': filtered_product_quantities,
            'title': f"Total Item Wise Consumption: {len(product_quantities)}",
            'start_date_str': start_date_str,
            'end_date_str': end_date_str
        }
        return render(request, 'medicine_store/itemwiseconsumptionn.html', context=context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def get_consumption_and_remaining_quantityyy(request):
    department = request.session.get('user_role')
    d = DrugDepartment.objects.filter(name=department).first()
    # Get the current time in UTC
    current_time_utc = timezone.now()
    # request.session['user_role'] = 'Registration'

    # Get the Kolkata timezone
    kolkata_timezone = pytz.timezone('Asia/Kolkata')

    # Convert the current time to Kolkata timezone
    current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)

    current_date = current_time_kolkata.date()
    today_date = current_date.strftime('%Y-%m-%d')

    if request.user.is_superuser or d is not None:
        start_date_str = request.GET.get('start_date', today_date)
        end_date_str = request.GET.get('end_date', today_date)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = None


        all_supplies = Supply.objects.filter(departpment=d).all()
        all_medicines = MedicineConsumption.objects.filter(departpment=d)

        product_quantities = {}
        if start_date and end_date:
            before_day = start_date - timedelta(days = 1)

            for supply in all_supplies:
                products = supply.products.all()
                for product in products:
                    product_name = product.product_name
                    if product_name not in product_quantities:
                        product_quantities[product_name] = {
                            'opening': 0,
                            'closing': 0,
                            'remaining_quantity': 0,
                            'purchase': 0
                        }
                    product_quantities[product_name]['purchase'] += product.quantity

            for product_name, quantities in product_quantities.items():
                # Opening Quantity
                total_opening_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_before_start = MedicineConsumption.objects.filter(
                    products__created_at__lte=start_date,
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_ = MedicineConsumption.objects.filter(
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_st_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__stock_quantity'))['total_quantity'] or 0

                total_edited = total_opening_quantity - total_consumed_ - total_st_quantity

                opening_quantity = total_opening_quantity - total_edited - total_consumed_before_start

                # Closing Quantity
                total_closing_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = department,
                    order_date__lte=start_date,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                first_end_date = datetime(2024, 4, 1)
                total_purchase_quantityy = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = None,
                    order_date__lt=start_date,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_till_end = MedicineConsumption.objects.filter(
                    products__created_at__range=[first_end_date, before_day],
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                

                closing_quantity = total_closing_quantity + total_purchase_quantityy - total_consumed_till_end 


                total_purchase_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = None,
                    order_date__range=[start_date, end_date],
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0


                total_purchase_quantity_ = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = department,
                    order_date__range=[start_date, end_date],
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0


                # Consumption within the date range
                total_consumed_in_range = MedicineConsumption.objects.filter(
                    products__created_at__range=[start_date, end_date],
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                
                print(product_name,total_closing_quantity, total_purchase_quantityy, total_consumed_till_end, total_consumed_in_range, total_edited)
                # print(start_date)
                purchase = total_purchase_quantity + total_purchase_quantity_
                if start_date.date() == datetime(2024, 4, 1).date():
                    print("#########")
                    closing_quantity = total_closing_quantity
                    purchase = total_purchase_quantity
                # Update quantities in the dictionary
                product_quantities[product_name]['purchase1'] = purchase
                product_quantities[product_name]['opening'] = closing_quantity 
                product_quantities[product_name]['closing'] = closing_quantity + purchase - total_consumed_in_range
                product_quantities[product_name]['remaining_quantity'] = total_consumed_in_range
        # print(product_quantities)
        # filtered_product_quantities = {k: v for k, v in product_quantities.items() if v['opening'] != 0}

        context = {
            'product_quantities': product_quantities,
            'title': f"Total Item Wise Consumption: {len(product_quantities)}",
            'start_date_str': start_date_str,
            'end_date_str': end_date_str
        }
        return render(request, 'medicine_store/itemwiseconsumptionnn.html', context=context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def get_consumption_and_remaining_quantityyy_data(request):
    department = request.session.get('user_role')
    d = DrugDepartment.objects.filter(name=department).first()
    # Get the current time in UTC
    current_time_utc = timezone.now()
    # request.session['user_role'] = 'Registration'

    # Get the Kolkata timezone
    kolkata_timezone = pytz.timezone('Asia/Kolkata')

    # Convert the current time to Kolkata timezone
    current_time_kolkata = current_time_utc.astimezone(kolkata_timezone)

    current_date = current_time_kolkata.date()
    today_date = current_date.strftime('%Y-%m-%d')

    if request.user.is_superuser or d is not None:
        start_date_str = request.GET.get('start_date', today_date)
        end_date_str = request.GET.get('end_date', today_date)

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = None

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = None

        before_day = end_date - timedelta(days = 1)

        all_supplies = Supply.objects.filter(departpment=d).all()
        all_medicines = MedicineConsumption.objects.filter(departpment=d)

        product_quantities = {}
        if start_date and end_date:
            for supply in all_supplies:
                products = supply.products.all()
                for product in products:
                    product_name = product.product_name
                    if product_name not in product_quantities:
                        product_quantities[product_name] = {
                            'opening': 0,
                            'closing': 0,
                            'remaining_quantity': 0,
                            'purchase': 0
                        }
                    product_quantities[product_name]['purchase'] += product.quantity

            for product_name, quantities in product_quantities.items():
                # Opening Quantity
                total_opening_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_before_start = MedicineConsumption.objects.filter(
                    products__created_at__lte=start_date,
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_ = MedicineConsumption.objects.filter(
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_st_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__stock_quantity'))['total_quantity'] or 0

                total_edited = total_opening_quantity - total_consumed_ - total_st_quantity

                if product_name == 'Diclofenac Sodium 50mg':
                    total_edited += 10

                opening_quantity = total_opening_quantity - total_edited - total_consumed_before_start

                # Closing Quantity
                total_closing_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    # order_date__range=[start_date, end_date],
                    order_date__lt=start_date,
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_purchase_quantityy = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    order_date__range=[start_date, end_date],
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                total_consumed_till_end = MedicineConsumption.objects.filter(
                    products__created_at__lt=start_date,
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0
                
                closing_quantity = total_closing_quantity + total_purchase_quantityy - total_consumed_till_end 


                total_purchase_quantity = Supply.objects.filter(
                    products__product_name=product_name,
                    departpment=d,
                    de = None,
                    order_date__range=[start_date, end_date],
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0


                # Consumption within the date range
                total_consumed_in_range = MedicineConsumption.objects.filter(
                    products__created_at__range=[start_date, end_date],
                    products__product__product_name=product_name,
                    departpment=d
                ).aggregate(total_quantity=Sum('products__quantity'))['total_quantity'] or 0

                print(product_name,total_closing_quantity, total_purchase_quantityy, total_consumed_till_end, total_consumed_in_range, total_edited)

                # print(start_date)
                # if start_date.date() == datetime(2024, 4, 1).date():
                #     print("#########")
                #     closing_quantity = total_closing_quantity
                # Update quantities in the dictionary
                product_quantities[product_name]['purchase1'] = total_purchase_quantity
                product_quantities[product_name]['opening'] = closing_quantity 
                product_quantities[product_name]['closing'] = closing_quantity + total_purchase_quantity - total_consumed_in_range
                product_quantities[product_name]['remaining_quantity'] = total_consumed_in_range
        # print(product_quantities)
        filtered_product_quantities = {k: v for k, v in product_quantities.items() if v['opening'] != 0}

        context = {
            'product_quantities': filtered_product_quantities,
            'title': f"Total Item Wise Consumption: {len(product_quantities)}",
            'start_date_str': start_date_str,
            'end_date_str': end_date_str
        }
        return render(request, 'medicine_store/itemwiseconsumption_data.html', context=context)
    else:
        logout(request)
        return redirect('signin')

@login_required
def store_expired_medicine(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        supplies = Supply.objects.filter(departpment=d).order_by('-order_date')

        # Initialize an empty list to store the expiring products
        expiring_products = []

        # Loop through each supply
        for supply in supplies:
            # Get the related ProductSupply instances for the current supply
            product_supplies = supply.products.all()

            # Loop through each product supply
            for product_supply in product_supplies:
                # Check if the exp_date is less than 3 months from today
                if product_supply.exp_date is not None and product_supply.exp_date <= timezone.now().date() + timedelta(days=3*30):
                    # If it is, add relevant details to the expiring_products list
                    expiring_products.append({
                        'product_type': product_supply.product_type,
                        'product_name': product_supply.product_name,
                        'mfg_name': product_supply.mfg_name,
                        'mfg_date': product_supply.mfg_date,
                        'exp_date': product_supply.exp_date,
                        'batch_no': product_supply.batch_no,
                        'stock_quantity': product_supply.stock_quantity,
                        'supply_date': product_supply.supply_date,
                    })
        d = DrugDepartment.objects.all()
        context = {
            'title' : f"Total Expired Medicine : {len(expiring_products)}",
            'expiring_products' : expiring_products
        }
        return render(request, 'medicine_store/exppired.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def store_expired_medicine_print(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        supplies = Supply.objects.filter(departpment=d).order_by('-order_date')

        # Initialize an empty list to store the expiring products
        expiring_products = []

        # Loop through each supply
        for supply in supplies:
            # Get the related ProductSupply instances for the current supply
            product_supplies = supply.products.all()

            # Loop through each product supply
            for product_supply in product_supplies:
                # Check if the exp_date is less than 3 months from today
                if product_supply.exp_date is not None and product_supply.exp_date <= timezone.now().date() + timedelta(days=3*30):
                    # If it is, add relevant details to the expiring_products list
                    expiring_products.append({
                        'product_type': product_supply.product_type,
                        'product_name': product_supply.product_name,
                        'mfg_name': product_supply.mfg_name,
                        'mfg_date': product_supply.mfg_date,
                        'exp_date': product_supply.exp_date,
                        'batch_no': product_supply.batch_no,
                        'stock_quantity': product_supply.stock_quantity,
                        'supply_date': product_supply.supply_date,
                    })
        d = DrugDepartment.objects.all()
        context = {
            'title' : f"Total Expired Medicine : {len(expiring_products)}",
            'expiring_products' : expiring_products
        }
        return render(request, 'medicine_store/expired_print.html', context=context)
    else:
        logout(request)
        return redirect('signin') 
