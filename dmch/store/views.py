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
def departments(request):
    if request.user.is_superuser:

        if request.method == "POST":
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            d = StoreDepartment(name = department, room_no = room_no)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = StoreDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : d,
            'title' : 'Departments'
        }
        return render(request, 'store/departments.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_update(request, department_id):
    if request.user.is_superuser:

        if request.method == "POST":
            d = StoreDepartment.objects.filter(department_id =department_id).first()
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            print(room_no)
            dc = StoreDepartment.objects.filter(name = department).first()
            if not dc or dc.name == department:
                d.name = department
                d.room_no = room_no
                d.save()
                messages.success(request, 'Department updated successfully.')
            else:
                messages.error(request, 'Department name already exists.')

        return redirect('store_departments')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_delete(request, department_id):
    if request.user.is_superuser:

        d = StoreDepartment.objects.filter(department_id =department_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('store_departments')
    else:
        logout(request)
        return redirect('signin') 



@login_required
def product_add_view(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            date = request.POST.get('date')
            bill_no = request.POST.get('bill_no')
            chalan_no = request.POST.get('chalan_no')
            bill_date = request.POST.get('bill_date')
            chalan_date = request.POST.get('chalan_date')
            sp_order_no = request.POST.get('sp_order_no')
            sp_order_date = request.POST.get('sp_order_date')
            received_date = request.POST.get('received_date')


            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_name = request.POST.get(f'product_name_{i}')
                company_name = request.POST.get(f'company_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')


                product = Product.objects.create(
                    user = request.user,
                    sdepartment=d,
                    created_at = date,
                    product_name = product_name,
                    company_name=company_name,
                    quantity=quantity,
                    stock_quantity = quantity,
                    bill_no = bill_no,
                    chalan_no = chalan_no,
                    bill_date = bill_date,
                    chalan_date = chalan_date,
                    sp_order_no = sp_order_no,
                    sp_order_date = sp_order_date,
                    received_date = received_date,
                )
            request.session['add_product_date'] = date
            request.session['received_date'] = received_date
            

            messages.success(request, 'Added Successfully')

        d = StoreDepartment.objects.all().order_by('-created_at')
        p = Product.objects.all().order_by('-created_at')
        context = {
            'title' : 'Add Product',
            'department' : d,
            'product' : p,
        }
        return render(request, 'store/add_product.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def product_delete_view(request, product_id):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        supply = get_object_or_404(Product, product_id=product_id)

        supply.delete()
        return redirect('product_details_view')  # Replace 'success-page' with actual URL
    else:
        logout(request)
        return redirect('signin') 

@login_required
def product_details_view(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') + timedelta(days=1)  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range
        if request.user.is_superuser:
            p = Product.objects.all().order_by('-created_at')
        else:
            p = Product.objects.filter(user=request.user, sdepartment = d).order_by('-created_at')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(created_at__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = StoreDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    p = p.filter(sdepartment = de)
                    print(p)
                    department = de.name


        d = StoreDepartment.objects.all()
        context = {
            'products' : p,
            'title' : f"Total Products : {len(p)}",
            'departments' : d
        }
        return render(request, 'store/show_products.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_details_view_print(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') + timedelta(days=1)  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range
        if request.user.is_superuser:
            p = Product.objects.all().order_by('-created_at')
        else:
            p = Product.objects.filter(user=request.user, sdepartment = d).order_by('-created_at')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(created_at__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = StoreDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    p = p.filter(sdepartment = de)
                    print(p)
                    department = de.name


        d = StoreDepartment.objects.all()
        context = {
            'products' : p,
            'title' : f"Total Supply : {len(p)}",
            'departments' : d
        }
        return render(request, 'store/products_print.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_update_view(request, supply_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        supply = get_object_or_404(Supply, supply_id=supply_id)
        print(supply)
        if request.method == 'POST':
            # Extract data from the form
            indent = request.POST.get('indent')
            department_id = request.POST.get('department_id')
            product_name = request.POST.get('product_name')
            product_type = request.POST.get('product_type')
            mfg_name = request.POST.get('mfg_name')
            batch_no = request.POST.get('batch_no')
            department = DrugDepartment.objects.filter(department_id=department_id).first()
            supply.department = department
            supply.indent = indent
            supply.save()

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


                print(f"Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")

                pp = ProductSupply.objects.filter(productdetails_id = product_name).first()
                if pp:
                    product_type = ProductType.objects.filter(product_type_id=pp.product.product_type_id).first()
                    p = ProductPurchase.objects.filter(product = product_type, batch_no = batch_no).first()
                    print(p)
                    if p:
                        print(p.stock_quantity, quantity)

                        if int(p.stock_quantity) >= int(quantity):
                            p.stock_quantity = int(p.stock_quantity) -  int(quantity) + p.stock_quantity
                            p.save()

                            pp.product = product_type
                            pp.mfg_name = mfg_name
                            pp.batch_no = batch_no
                            pp.quantity = quantity
                            pp.mfg_date = mfgdate
                            pp.exp_date = expdate
                            pp.stock_quantity = quantity
                            pp.supply_date = date

                            pp.save()

                if pp is not None:
                    try:
                        product_type = ProductType.objects.filter(product_type_id=pp.product.product_type_id).first()
                        p = ProductPurchase.objects.filter(product = product_type, batch_no = batch_no).first()
                        print(p)
                        if p:
                            print(p.stock_quantity, quantity)

                            if int(p.stock_quantity) >= int(quantity):
                                p.stock_quantity = int(p.stock_quantity) -  int(quantity)
                                p.save()

                                product = ProductSupply.objects.create(
                                    user = request.user,
                                    product=product_type,
                                    mfg_name=mfg_name,
                                    batch_no=batch_no,
                                    quantity=quantity,
                                    mfg_date = mfgdate,
                                    exp_date = expdate,
                                    stock_quantity = stock_quantity,
                                    supply_date = date
                                )

                                supply.products.add(product)
                    except Exception as e:
                        print(e)

            # Save the order
            supply.save()
            messages.success(request, 'Updated Successfully')

        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct()
        context = {
            'title' : 'Update Supply',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types,
            'supply' : supply,
        }
        return render(request, 'update_supply.html', context=context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def get_product_details_view(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        # Get the selected product type from the AJAX request
        product_name = request.GET.get('product_name')
        print(product_name)
        if product_name:
            # Retrieve the ProductPurchase object
            product_purchase = Product.objects.filter(product_id=product_name).first()
            print(product_purchase)
            # Check if the ProductPurchase object exists
            if product_purchase:
                # Convert the model instance to a dictionary
                product_purchase_dict = model_to_dict(product_purchase)
                # Return the dictionary as JSON response
                return JsonResponse({'product': product_purchase_dict})
        else:
            # If no product purchase found, return empty response or appropriate error message
            return JsonResponse({'error': 'Product purchase not found for the given product name'}, status=404)

    else:
        logout(request)
        return redirect('signin') 


@login_required
def product_add_consumption(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            date = request.POST.get('date')
            department = request.POST.get('department')
            indent_no = request.POST.get('indent_no')


            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                product_name = request.POST.get(f'product_name_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                p = Product.objects.filter(product_id = product_name).first()
                print(p, p.product_name)
                if p is not None:
                    if int(quantity) < p.stock_quantity:
                        product = ProductConsumption.objects.create(
                            user = request.user,
                            sdepartment=d,
                            department = department,
                            indent_no = indent_no,
                            created_at = date,
                            product_name = p.product_name,
                            company_name = p.company_name,
                            quantity = quantity,
                            stock_quantity = quantity,
                            bill_no = p.bill_no,
                            chalan_no = p.chalan_no,
                            bill_date = p.bill_date,
                            chalan_date = p.chalan_date,
                            sp_order_no = p.sp_order_no,
                            sp_order_date = p.sp_order_date,
                            received_date = p.received_date
                        )
                        p.stock_quantity = p.stock_quantity - int(quantity)
                        p.save()
            request.session['add_product_date'] = date
            

            messages.success(request, 'Added Successfully')

        sd = StoreDepartment.objects.all().order_by('-created_at')
        p = Product.objects.filter(sdepartment = d).order_by('-created_at')
        context = {
            'title' : 'Transfer Product',
            'department' : sd,
            'product' : p,
        }
        return render(request, 'store/add_consumption.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def product_consumption_delete_view(request, product_id):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:
        supply = get_object_or_404(ProductConsumption, product_id=product_id)

        supply.delete()
        return redirect('product_consumption_details_view')  # Replace 'success-page' with actual URL
    else:
        logout(request)
        return redirect('signin') 

@login_required
def product_consumption_details_view(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') + timedelta(days=1)  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range
        if request.user.is_superuser:
            p = ProductConsumption.objects.all().order_by('-created_at')
        else:
            p = ProductConsumption.objects.filter(user=request.user, sdepartment = d).order_by('-created_at')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(created_at__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = StoreDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    p = p.filter(sdepartment = de)
                    print(p)
                    department = de.name


        d = StoreDepartment.objects.all()
        context = {
            'products' : p,
            'title' : f"Total Products : {len(p)}",
            'departments' : d
        }
        return render(request, 'store/show_products_consumption.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def product_consumption_details_view_print(request):
    departpment = request.session['user_role']
    d = StoreDepartment.objects.filter(name = departpment).first()
    if request.user.is_superuser or d is not None:

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        department_id = request.GET.get('department')
        # o = Order.objects.all()
        # Convert the date strings to datetime objects
        if start_date_str:
            # start_date = current_time_kolkata.strptime(start_date_str, '%Y-%m-%d')
            start_date = start_date_str
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')

        else:
            start_date = None

        if end_date_str:
            # end_date = current_time_kolkata.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date_str
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M') + timedelta(days=1)  # Add one day to include end_date

            # Adjust the end date to include all records for that day
            # end_date = end_date + timedelta(days=1)  # Include records for the entire day
        else:
            end_date = None
        
        # Filter patients based on the provided date range
        if request.user.is_superuser:
            p = ProductConsumption.objects.all().order_by('-created_at')
        else:
            p = ProductConsumption.objects.filter(user=request.user, sdepartment = d).order_by('-created_at')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(created_at__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(created_at__gte=start_datetime, created_at__lt=end_datetime)
        elif end_date:
            p = p.filter(created_at__lt=end_date)

        department = None
        if department_id != None:
            if department_id != 'All':
                de = StoreDepartment.objects.filter(department_id = department_id).first()
                print(de)
                if de:
                    p = p.filter(sdepartment = de)
                    print(p)
                    department = de.name


        d = StoreDepartment.objects.all()
        context = {
            'products' : p,
            'title' : f"Total Supply : {len(p)}",
            'departments' : d
        }
        return render(request, 'store/products_consumption_print.html', context=context)

    else:
        logout(request)
        return redirect('signin') 
