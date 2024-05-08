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


@login_required
def supply_details_view(request):
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
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
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
            'title' : f"Stock : {len(p)}",
            'departments' : d,
            'department' : department,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/stock.html', context=context)
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
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT') + timedelta(days=1)  # Add one day to include end_date

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
            'title' : f"Stock",
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
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Add one day to include end_date

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
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/stock.html', context=context)
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
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)  # Add one day to include end_date

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
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/rstockprint.html', context=context)
    else:
        logout(request)
        return redirect('signin') 



@login_required
def get_medicine_names_by_type(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or request.session['user_role'] == 'Drug' or request.session['user_role_store'] == 'Medicine Store' :

        # Get the selected product type from the AJAX request
        product_type = request.GET.get('product_type')

        # Query the database to retrieve product names based on the selected product type

        # Create a list to store the product names
        product_names = []

        unique_p_types = []
        ss = Supply.objects.all()
        # print(ss)
        for s in ss:
            # print(s.departpment, d)
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    if ps.stock_quantity > 0:
                        print(product_type, ps.product_type)
                        if product_type == ps.product_type:
                            print("#########")
                            print(product_type, ps.product_type)
                            unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'name' : ps.product_name })
        print(unique_p_types)

        # Return the product names as JSON response
        return JsonResponse({'products': unique_p_types})
    else:
        logout(request)
        return redirect('signin') 

@login_required
def medicine_supply_add_view(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            regid = request.POST.get('regid', None)
            patient_name = request.POST.get('patient_name', None)
            date = request.POST.get(f'date')
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

            if p is None:
                p = Patient.objects.create(
                    user = request.user,
                    gender = '',
                    de = departpment
                )
                if regid:
                    p.regnoid = regid
                if patient_name:
                    p.name = patient_name
                p.save()
            print(p)
            
            # Create a new supply instance
            m = MedicineConsumption.objects.create(
                user = request.user,
                patient=p,
                created_at = date
            )

            request.session['supply_date'] = date

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
                    if int(ps.stock_quantity) >= int(quantity):
                        ps.stock_quantity = int(ps.stock_quantity) -  int(quantity)
                        ps.save()
                        product = Medicine.objects.create(
                            product = ps,
                            quantity=quantity,
                            created_at = date
                        )
                        m.created_at = date
                        
                        m.products.add(product)
                    
            # Save the order
            m.save()
            messages.success(request, 'Added Successfully')

        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        sp = ProductSupply.objects.all().order_by('-created_at')

        unique_p_typess = ProductType.objects.values_list('p_type', flat=True).distinct()
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True)
        # ss = Supply.objects.filter(departpment=d).order_by('-order_date')
        # unique_p_types = ss.products.all()

        unique_p_types = []
        ss = Supply.objects.all()
        print(ss)
        for s in ss:
            print(s.departpment, d)
            if s.departpment.name == departpment:
                sp = s.products.all()
                for ps in sp:
                    if ps.stock_quantity > 0:
                        unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
        print(unique_p_types)

        context = {
            'title' : 'Medicine Consumption / Supply',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_typess,
            'productsupply' : unique_p_types
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

        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            regid = request.POST.get('regid', None)
            patient_name = request.POST.get('patient_name', None)
            date = request.POST.get(f'date')
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

            # if p is None:
            #     p = Patient.objects.create(
            #         user = request.user,
            #         gender = '',
            #         de = departpment
            #     )
            #     if regid:
            #         p.regnoid = regid
            #     if patient_name:
            #         p.name = patient_name
            #     p.save()
            # print(p)
            
            # Create a new supply instance
            # m = MedicineConsumption.objects.create(
            #     user = request.user,
            #     patient=p,
            #     created_at = date
            # )
            m = MedicineConsumption.objects.filter(consumption_id = consumption_id, user = request.user).first()

            request.session['supply_date'] = date

            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                medicine_id = request.POST.get(f'medicine_id_{i}')

                ps = ProductSupply.objects.filter(productdetails_id = product_name).first()
                print(ps)
                med = Medicine.objects.filter(medicine_id = medicine_id).first()
                print(med)
                if med:
                    print(quantity)
                    if int(med.product.stock_quantity) >= int(quantity):
                        if med.product.productdetails_id == ps.productdetails_id:
                            quantity_m = int(med.product.stock_quantity) +  int(med.quantity) - int(quantity)
                            med.product.stock_quantity = quantity_m
                            med.product.save()
                            med.quantity = quantity
                            med.created_at = date
                            med.save()
                        else:
                            med.product.stock_quantity = int(med.product.stock_quantity) +  int(med.quantity)
                            med.product.save()
                            if int(ps.stock_quantity) >= int(quantity):
                                ps.stock_quantity = int(ps.stock_quantity) -  int(quantity)
                                ps.save()
                                med.product = ps
                                med.quantity = quantity
                                med.save()
                                
            messages.success(request, 'Updated Successfully')

        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        sp = ProductSupply.objects.all().order_by('-created_at')
        medicine = get_object_or_404(MedicineConsumption, consumption_id=consumption_id)

        unique_p_typess = ProductSupply.objects.values_list('product_type', flat=True).distinct()
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True)
        # ss = Supply.objects.filter(departpment=d).order_by('-order_date')
        # unique_p_types = ss.products.all()

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

        context = {
            'title' : 'Medicine Consumption / Supply',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_typess,
            'productsupply' : unique_p_types,
            'medicine' : medicine,
            'total' : len(medicine.products.all())
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
        m = MedicineConsumption.objects.filter(consumption_id = consumption_id, user = request.user).first()
        if m is not None:
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
    # Get the selected product type from the AJAX request
    product_name = request.GET.get('product_name')
    print(product_name)
    if product_name:
        # Retrieve the ProductPurchase object
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
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
        else:
            start_date = None

        if end_date_str:
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') + timedelta(days=1)
        else:
            end_date = None
        
        p = MedicineConsumption.objects.filter(user = request.user).order_by('-created_at')

        if start_date and end_date:
            p = p.filter(created_at__range=(start_date, end_date))

        elif start_date:
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)

        elif end_date:
            p = p.filter(created_at__lt=end_date)

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
            'title' : f"Total Medicine Consumption : {len(p)}",
            'departments' : d,
            'productsupply' : unique_p_types

        }
        return render(request, 'medicine_store/supplydetails.html', context=context)

    else:
        logout(request)
        return redirect('signin') 


@login_required
def supply_details_user_view_print(request):
    departpment = request.session['user_role']
    d = DrugDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')

        if start_date_str:
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
        else:
            start_date = None

        if end_date_str:
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') + timedelta(days=1)
        else:
            end_date = None
        
        p = MedicineConsumption.objects.filter(user = request.user).order_by('-created_at')

        if start_date and end_date:
            p = p.filter(created_at__range=(start_date, end_date))

        elif start_date:
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)
            p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)

        elif end_date:
            p = p.filter(created_at__lt=end_date)

        d = DrugDepartment.objects.all()
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
            'title' : f"Total Medicine Consumption : {len(p)}",
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
            product_name = request.POST.get('product_name')
            product_type = request.POST.get('product_type')
            mfg_name = request.POST.get('mfg_name')
            batch_no = request.POST.get('batch_no')

            department = DrugDepartment.objects.filter(department_id=department_id).first()


            # supply.department = department
            # supply.indent = indent
            # supply.save()

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

                pp = ProductSupply.objects.filter(productdetails_id = productdetails_id, department = d).first()
                if pp:
          
                    pp.mfg_name = mfg_name
                    pp.batch_no = batch_no
                    pp.quantity = quantity
                    if mfgdate:
                        pp.mfg_date = mfgdate
                    if expdate:
                        pp.exp_date = expdate
                    pp.stock_quantity = stock_quantity
                    pp.supply_date = date

                    pp.save()

            # Save the order
            supply.save()
            messages.success(request, 'Updated Successfully')

        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct()
        # unique_p_types = ProductSupply.objects.all().order_by('-created_at')
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
    

# @login_required
# def get_consumption_and_remaining_quantity(request):
#     departpment = request.session['user_role']
#     d = DrugDepartment.objects.filter(name = departpment).first()
#     if request.user.is_superuser or d is not None:

#         start_date_str = request.GET.get('start_date', None)
#         end_date_str = request.GET.get('end_date', None)
#         product_name = request.GET.get('product_name', None)

#         if start_date_str:
#             start_date = start_date_str
#             start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
#         else:
#             start_date = None

#         if end_date_str:
#             end_date = end_date_str
#             end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
#         else:
#             end_date = None
#         asu = Supply.objects.filter(departpment=d).order_by('-order_date')
#         # print(a)
#         p = []

#         products = []
#         for ap in asu:
#             ps = ap.products.all()
#             department = None
#             if product_name != None:
#                 if product_name != 'All':
#                     ps = ps.filter(productdetails_id = product_name)
#                     # print(ps)
#                     if ps:
#                         department = ps[0].productdetails_id
            
#             for a in ps:

#                 if a is not None:
#                     productt_name = a.product_name
#                     quantity = a.quantity
#                     if start_date:
#                         # Check if the product name is already present in the list
#                         found_product = next((p for p in products if p['product'] == productt_name), None)

#                         if found_product:
#                             # If the product is found, add its quantity to the existing entry
#                             found_product['total_quantity'] += quantity
#                         else:
#                             # If the product is not found, add a new entry to the products list
#                             products.append({
#                                 'product': product_name,
#                                 'total_quantity': quantity,
#                                 'end_total_quantity': 0,
#                                 'till_remaining': 0,
#                                 'till_end': 0,
#                                 'till_today' : 0
#                             })

#                         if start_date and end_date:
#                             next_day = end_date + timedelta(days=1)
#                             prev_day = start_date - timedelta(days=1)
#                             total_quantity = Medicine.objects.filter(product=a, created_at__lt=prev_day).aggregate(total_quantity=Sum('quantity'))['total_quantity']
#                             end_total_quantity = Medicine.objects.filter(product=a, created_at__lt=next_day).aggregate(total_quantity=Sum('quantity'))['total_quantity']
    
#                             # total_quantity = Medicine.objects.filter(product=a, created_at__lt=start_datetime).aggregate(total_quantity=Sum('quantity'))['total_quantity']
#                             # end_total_quantity = Medicine.objects.filter(product=a, created_at__lt=end_datetime).aggregate(total_quantity=Sum('quantity'))['total_quantity']
#                             print("Total Quantity:", total_quantity)
#                             print("End Total Quantity:", end_total_quantity)
#                             till_today = 0
#                             till_remaining = 0
#                             till_end = 0
#                             # print(total_quantity, end_total_quantity)
#                             for info in products:
#                                 if info['product'] == product_name:
#                                     if end_total_quantity is None:
#                                         end_total_quantity = 0
#                                     if total_quantity is None:
#                                         total_quantity = 0
#                                     # till_today = end_total_quantity
                                    
#                                     till_remaining = info['total_quantity'] - total_quantity
#                                     till_end = info['total_quantity'] - end_total_quantity
#                                     # print(till_today, till_remaining, till_end)
#                             # if total_quantity > 0:
#                             p.append({
#                                 'product': a.product_name,
#                                 'total_quantity': end_total_quantity - total_quantity,
#                                 'end_total_quantity': end_total_quantity,
#                                 'till_remaining': till_remaining,
#                                 'till_end': till_end,
#                                 'till_today' : till_today
#                             })
                    


#                 # elif end_date:
#                 #     total_quantity = Medicine.objects.filter(product=a, created_at__lt=end_date).aggregate(total_quantity=Sum('quantity'))['total_quantity']
#                 #     p.append({
#                 #         'product' : a.product.name,
#                 #         'total_quantity' : total_quantity
#                 #     })
#         # print(p)
#         # print([p])
#         d = DrugDepartment.objects.all()
#         # sp = ProductSupply.objects.values('product_name', 'productdetails_id').distinct()
#         unique_p_types = []
#         ss = Supply.objects.all()
#         # print(ss)
#         for s in ss:
#             if s.departpment.name == departpment:
#                 sp = s.products.all()
#                 for ps in sp:
#                     unique_p_types.append({'productdetails_id' : ps.productdetails_id , 'product_name' : ps.product_name })
#         # print(unique_p_types)
#         context = {
#             'supply' : p,
#             'title' : f"Total Item Wise Consumption : {len(p)}",
#             'departments' : d,
#             'department' : product_name,
#             'productsupply' : unique_p_types,
#             'start_date_str' : start_date_str,
#             'end_date_str' : end_date_str
#         }

#         return render(request, 'medicine_store/itemwiseconsumption.html', context=context)

#     else:
#         logout(request)
#         return redirect('signin') 
    
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
            date = request.POST.get('date')

            # department = DrugDepartment.objects.filter(department_id=department_id).first()

            # Create a new supply instance
            supply = Supply.objects.create(
                user = request.user,
                departpment=d,
                indent  = indent,
                de = departpment,
                remarks = remarks,
                order_date = date
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
                    supply_date = date,
                    department = d
                    
                )
                print(expdate, mfgdate)
                if mfgdate is not None and mfgdate != '':
                    product.mfg_date = mfgdate
                if expdate is not None and expdate != '':
                    product.exp_date = expdate
                product.save()
                supply.products.add(product)
                request.session['stock_date'] = date
            # Save the order
            supply.save()
            messages.success(request, 'Added Successfully')

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
        unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct()

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
        supply = get_object_or_404(Supply, supply_id=supply_id)
        supply.delete()
        return redirect('medicine_supply_details_view') 
    else:
        logout(request)
        return redirect('signin') 


@login_required
def get_consumption_and_remaining_quantity(request):
    department = request.session.get('user_role')  # Using .get() to safely get the value without raising an error if it doesn't exist
    d = DrugDepartment.objects.filter(name=department).first()

    if request.user.is_superuser or d:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        product_name = request.GET.get('product_name', None)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) if end_date_str else None

        asu = Supply.objects.filter(departpment=d).order_by('-order_date')
        p = []

        for ap in asu:
            ps = ap.products.all()

            if product_name and product_name != 'All':
                ps = ps.filter(productdetails_id=product_name)

            for a in ps:
                productt_name = a.product_name
                quantity = a.quantity

                if start_date and end_date:
                    prev_day = start_date - timedelta(days=1)
                    next_day = end_date + timedelta(days=1)
                    m = Medicine.objects.filter(product = a).all()

                    total_quantity = m.filter(created_at__lt=prev_day).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                    end_total_quantity = m.filter(created_at__lt=next_day).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

                    till_remaining = quantity - total_quantity
                    till_end = quantity - end_total_quantity
                    t_quantity = end_total_quantity - total_quantity
                    if t_quantity > 0:
                        p.append({
                            'product': a.product_name,
                            'total_quantity': end_total_quantity - total_quantity,
                            'end_total_quantity': end_total_quantity,
                            'till_remaining': till_remaining,
                            'till_end': till_end,
                            'till_today': 0  # till_today is not calculated in the provided code, so it's set to 0
                        })

        d = DrugDepartment.objects.all()

        unique_p_types = []
        for s in Supply.objects.filter(departpment__name=department):
            sp = s.products.all()
            for ps in sp:
                unique_p_types.append({'productdetails_id': ps.productdetails_id, 'product_name': ps.product_name})

        context = {
            'supply': p,
            'title': f"Total Item Wise Consumption : {len(p)}",
            'departments': d,
            'department': product_name,
            'productsupply': unique_p_types,
            'start_date_str': start_date_str,
            'end_date_str': end_date_str
        }

        return render(request, 'medicine_store/itemwiseconsumption.html', context=context)
    else:
        logout(request)
        return redirect('signin')
