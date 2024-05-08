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
from django.db.models import Sum
from django.db.models.functions import Lower, Upper, Trim
from django.db.models import CharField
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
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        if request.method == "POST":
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            d = DrugDepartment(name = department, room_no = room_no)
            d.save()
            messages.success(request, 'Department added successfully.')
        d = DrugDepartment.objects.all().order_by('-created_at')
        context = {
            'departments' : d,
            'title' : 'Departments'
        }
        return render(request, 'departments.html', context = context)
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_update(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        if request.method == "POST":
            d = DrugDepartment .objects.filter(department_id =department_id).first()
            department = request.POST['department']
            room_no = request.POST.get('room_no', None)
            print(room_no)
            dc = DrugDepartment.objects.filter(name = department).first()
            if not dc or dc.name == department:
                d.name = department
                d.room_no = room_no
                d.save()
                messages.success(request, 'Department updated successfully.')
            else:
                messages.error(request, 'Department name already exists.')

        return redirect('drug_departments')
    else:
        logout(request)
        return redirect('signin') 
    
@login_required
def departments_delete(request, department_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        d = DrugDepartment.objects.filter(department_id =department_id).first()
        d.delete()
        messages.success(request, 'Department deleted successfully.')

        return redirect('drug_departments')
    else:
        logout(request)
        return redirect('signin') 


# Supplier views
@login_required
def suppliar_add_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        if request.method == 'POST':
            name = request.POST.get('name')
            mobile = request.POST.get('mobile')
            gst = request.POST.get('gst')
            email = request.POST.get('email')
            address = request.POST.get('address')
            suppliar = Suppliar.objects.create(
                name=name,
                mobile=mobile,
                gst=gst,
                email=email,
                address=address
            )
            messages.success(request, 'Supplier Added Successfully')

        s = Suppliar.objects.all().order_by('-created_at')
        context = {
            'suppliar' : s,
            'title' : f"Total Supplier : {len(s)}"
        }
        return render(request, 'suppliar.html', context = context)

@login_required
def suppliar_update_view(request, suppliar_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        suppliar = get_object_or_404(Suppliar, suppliar_id=suppliar_id)
        if request.method == 'POST':
            suppliar.name = request.POST.get('name')
            suppliar.mobile = request.POST.get('mobile')
            suppliar.gst = request.POST.get('gst')
            suppliar.email = request.POST.get('email')
            suppliar.address = request.POST.get('address')
            suppliar.save()
            messages.success(request, 'Supplier Updated Successfully')
        return redirect('suppliar-add')
    else:
        logout(request)
        return redirect('signin') 

@login_required  
def suppliar_delete_view(request, suppliar_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        suppliar = get_object_or_404(Suppliar, suppliar_id=suppliar_id)
        suppliar.delete()
        messages.success(request, 'Supplier Deleted Successfully')
        return redirect('suppliar-add')
    else:
        logout(request)
        return redirect('signin') 


@login_required
def product_type_add_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug' :

        if request.method == 'POST':
            name = request.POST.get('name')
            p_type = request.POST.get('p_type')
            product_type = ProductType.objects.create(
                name=name,
                p_type=p_type
            )
            messages.success(request, 'Product Added Successfully')

        s = ProductType.objects.all().order_by('-created_at')
        context = {
            'producttype' : s,
            'title' : f"Total Products : {len(s)}"

        }
        return render(request, 'product_type.html', context = context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def product_type_update_view(request, product_type_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug' :

        product_type = get_object_or_404(ProductType, product_type_id=product_type_id)
        if request.method == 'POST':
            product_type.name = request.POST.get('name')
            product_type.p_type = request.POST.get('p_type')
            product_type.save()
        return redirect('product-type-add')
    else:
        logout(request)
        return redirect('signin') 

@login_required
def product_type_delete_view(request, product_type_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug' :

        product_type = get_object_or_404(ProductType, product_type_id=product_type_id)

        product_type.delete()
        return redirect('product-type-add')  
    else:
        logout(request)
        return redirect('signin') 

# Add view
@login_required
def order_add_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        if request.method == 'POST':
            print(request)
            print(request.POST)
            order_id = request.POST.get('order_id')
            suppliar_id = request.POST.get('suppliar')
            mob_no = request.POST.get('mob_no')
            gst = request.POST.get('gst')
            email = request.POST.get('email')

            # Assuming suppliar_name is the name of the suppliar selected from the dropdown
            suppliar = Suppliar.objects.filter(suppliar_id=suppliar_id).first()

            order = Order.objects.create(
                user = request.user,
                order_id=order_id,
                supplier=suppliar,
                mob_no=mob_no,
                gst=gst,
                email=email
            )

            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                department_name = request.POST.get(f'department_{i}')
                product_type_name = request.POST.get(f'product_type_{i}')
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                quantity = request.POST.get(f'quantity_{i}')

                print(f"Product[i]: Department ID: {department_name}, Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")

                print(department_name, product_type_name, product_name, mfg_name, batch_no)
                department = DrugDepartment.objects.filter(department_id=department_name).first()
                product_type = ProductType.objects.filter(product_type_id=product_name).first()
                product = ProductDetails.objects.create(
                    user = request.user,
                    department=department,
                    product=product_type,
                    mfg_name=mfg_name,
                    batch_no=batch_no,
                    quantity=quantity
                )

                order.products.add(product)
            messages.success(request, 'Order Added Successfully.')
            # Save the order
            order.save()
            messages.success(request, 'Added Successfully')


        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct()
        unique_p_types = ProductType.objects.annotate(
            normalized_p_type=Trim(Upper('p_type', output_field=CharField()))
        ).values_list('normalized_p_type', flat=True).distinct()

        context = {
            'title' : 'Add Order',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types
        }
        return render(request, 'add_order.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def order_details_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            o = Order.objects.all().order_by('-order_date')
        else:
            o = Order.objects.filter(user=request.user).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            o = o.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            o = o.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
        elif end_date:
            o = o.filter(order_date__lt=end_date)


        d = DrugDepartment.objects.all()
        context = {
            'orders' : o,
            'title' : f"Total Orders : {len(o)}",
        }
        return render(request, 'orders.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def order_details_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            o = Order.objects.all().order_by('-order_date')
        else:
            o = Order.objects.filter(user=request.user).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            o = o.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            o = o.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
        elif end_date:
            o = o.filter(order_date__lt=end_date)


        d = DrugDepartment.objects.all()
        context = {
            'orders' : o,
            'title' : f"Total Orders : {len(o)}",
        }
        return render(request, 'ordersprint.html', context=context)

    else:
        logout(request)
        return redirect('signin') 

@login_required
def get_product_names_by_type(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug' or request.session['user_role_store'] == 'Medicine Store' :

        # Get the selected product type from the AJAX request
        product_type = request.GET.get('product_type')

        # Query the database to retrieve product names based on the selected product type
        products = ProductType.objects.filter(p_type=product_type)

        # Create a list to store the product names
        product_names = []

        # Iterate over the retrieved products and extract their names
        for product in products:
            product_names.append({'product_type_id': product.product_type_id, 'name': product.name})

        # Return the product names as JSON response
        return JsonResponse({'products': product_names})
    else:
        logout(request)
        return redirect('signin') 

@login_required
def get_product_names_by_type_purchase(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        # Get the selected product type from the AJAX request
        product_type = request.GET.get('product_type')

        # Query the database to retrieve product names based on the selected product type
        products = ProductType.objects.filter(p_type=product_type)
        product_names = []
        for p in products:
            print(p)
            pdp = ProductPurchase.objects.filter(product=p)
            print(pdp)
            if pdp:
                for pp in pdp:
                    if pp.quantity > 0 and pp.stock_quantity > 0:
                        # Create a dictionary to store the product names
                        print(pp.productdetails_id , p.name)
                        product_names.append({'product_type_id': pp.productdetails_id, 'product_type_id_': p.product_type_id,  'name': p.name})
        # Return the product names as JSON response
        return JsonResponse({'products': product_names})
    else:
        logout(request)
        return redirect('signin') 

@login_required
def get_product_details(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        # Get the selected product type from the AJAX request
        product_name = request.GET.get('product_name')
        print(product_name)
        if product_name:
            # Retrieve the ProductPurchase object
            product_purchase = ProductPurchase.objects.filter(productdetails_id=product_name).first()
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

# Update view
@login_required
def order_update_view(request, order_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        order = get_object_or_404(Order, ord_id=order_id)

        if request.method == 'POST':
            print(request)
            print(request.POST)
            order_id = request.POST.get('order_id')
            suppliar_id = request.POST.get('suppliar')
            mob_no = request.POST.get('mob_no')
            gst = request.POST.get('gst')
            email = request.POST.get('email')

            # Assuming suppliar_name is the name of the suppliar selected from the dropdown
            suppliar = Suppliar.objects.filter(suppliar_id=suppliar_id).first()

            order.suppliar = suppliar
            order.gst = gst
            print(request.POST.get('product_count'))
            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                print(i)
                department_name = request.POST.get(f'department_{i}')
                product_type_name = request.POST.get(f'product_type_{i}')
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                productdetails_id = request.POST.get(f'productdetails_id_{i}')

                print(f"Product[i]: Department ID: {department_name}, Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")

                print(department_name, product_type_name, product_name, mfg_name, batch_no, productdetails_id)
                department = DrugDepartment.objects.filter(department_id=department_name).first()
                product_type = ProductType.objects.filter(product_type_id=product_name).first()
                
                p = ProductDetails.objects.filter(productdetails_id = productdetails_id).first()

                if p:
                    p.department = department
                    p.product = product_type
                    p.mfg_name = mfg_name
                    p.batch_no = batch_no
                    p.quantity = quantity
                    p.save()

                if p is None:
                    try:
                        if len(p)>0:
                            product = ProductDetails.objects.create(
                                user = request.user,
                                department=department,
                                product=product_type,
                                mfg_name=mfg_name,
                                batch_no=batch_no,
                                quantity=quantity
                            )

                            order.products.add(product)
                    except Exception as e:
                        print(e)

            messages.success(request, 'Order Added Successfully.')
            # Save the order
            order.save()
            messages.success(request, 'Added Successfully')


        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct()
        context = {
            'title' : 'Update Order',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types,
            'order' : order
        }
        return render(request, 'update_order.html', context=context)

    else:
        logout(request)
        return redirect('signin') 


# Delete view
@login_required
def order_delete_view(request, order_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        order = get_object_or_404(Order, ord_id=order_id)

        # Delete the order instance
        order.delete()
        # Redirect to a success page or another view
        return redirect('order_details_view')

    else:
        logout(request)
        return redirect('signin') 

@login_required
def purchase_add_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        if request.method == 'POST':
            # Extract data from the form
            order_id = request.POST.get('order_id')
            supplier_id = request.POST.get('suppliar')
            mob_no = request.POST.get('mob_no')
            gst = request.POST.get('gst')
            email = request.POST.get('email')
            invoice_no = request.POST.get('invoice')
            invoice_date = request.POST.get('invoice_date')
            total_amount = request.POST.get('total_amount')
            paid = request.POST.get('paid')
            due = request.POST.get('due')
            date = request.POST.get('date')
            # Create a new purchase instance
            suppliar = Suppliar.objects.filter(suppliar_id=supplier_id).first()

            purchase = Purchase.objects.create(
                user = request.user,
                order_id=order_id,
                supplier=suppliar,
                mob_no=mob_no,
                gst=gst,
                email=email,
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                total_amount=total_amount,
                paid=paid,
                due=due
            )
                    # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                department_name = request.POST.get(f'department_{i}')
                product_type_name = request.POST.get(f'product_type_{i}')
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                mrp = request.POST.get(f'mrp_{i}')
                purchaserate = request.POST.get(f'purchaserate_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                amount = request.POST.get(f'amount_{i}')
                date = request.POST.get(f'date_{i}')

                print(f"Product[i]: Department ID: {department_name}, Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")

                print(department_name, product_type_name, product_name, mfg_name, batch_no)
                department = DrugDepartment.objects.filter(department_id=department_name).first()
                product_type = ProductType.objects.filter(product_type_id=product_name).first()
                product = ProductPurchase.objects.create(
                    user = request.user,
                    department=department,
                    product = product_type,
                    product_name=product_type.name,
                    product_type=product_type.p_type,
                    mfg_name=mfg_name,
                    batch_no=batch_no,
                    quantity=quantity,
                    stock_quantity=quantity,
                    mfg_date = mfgdate,
                    exp_date = expdate,
                    mrp = mrp, 
                    purchase_rate = purchaserate,
                    purchase_amount = amount,
                    purchase_date = date
                )

                purchase.products.add(product)
            messages.success(request, 'Product Purchased Successfully.')

            # Save the order
            purchase.save()
            messages.success(request, 'Added Successfully')


        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        # unique_p_types = ProductType.objects.values_list('p_type', flat=True).distinct()
        unique_p_types = ProductType.objects.annotate(
            normalized_p_type=Trim(Upper('p_type', output_field=CharField()))
        ).values_list('normalized_p_type', flat=True).distinct()

        context = {
            'title' : 'Add Purchase',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types
        }
        return render(request, 'add_purchase.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def purchase_update_view(request,purchase_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        purchase = get_object_or_404(Purchase, purchase_id=purchase_id)

        if request.method == 'POST':
            # Extract data from the form
            order_id = request.POST.get('order_id')
            supplier_id = request.POST.get('suppliar')
            mob_no = request.POST.get('mob_no')
            gst = request.POST.get('gst')
            email = request.POST.get('email')
            invoice_no = request.POST.get('invoice')
            invoice_date = request.POST.get('invoice_date')
            total_amount = request.POST.get('total_amount')
            paid = request.POST.get('paid')
            due = request.POST.get('due')
            date = request.POST.get('date')
            suppliar = Suppliar.objects.filter(suppliar_id=supplier_id).first()

            purchase.suppliar = suppliar
            purchase.mob_no = mob_no
            purchase.gst = gst
            purchase.invoice_no = invoice_no
            purchase.invoice_date = invoice_date


            # Loop through the product form fields
            for i in range(1, int(request.POST.get('product_count')) + 1):
                department_name = request.POST.get(f'department_{i}')
                product_type_name = request.POST.get(f'product_type_{i}')
                product_name = request.POST.get(f'product_name_{i}')
                mfg_name = request.POST.get(f'mfgname_{i}')
                batch_no = request.POST.get(f'batchno_{i}')
                mfgdate = request.POST.get(f'mfgdate_{i}')
                expdate = request.POST.get(f'expdate_{i}')
                mrp = request.POST.get(f'mrp_{i}')
                purchaserate = request.POST.get(f'purchaserate_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                amount = request.POST.get(f'amount_{i}')
                productdetails_id = request.POST.get(f'productdetails_id_{i}')

                print(f"Product[i]: Department ID: {department_name}, Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")

                print(department_name, product_type_name, product_name, mfg_name, batch_no)
                department = DrugDepartment.objects.filter(department_id=department_name).first()
                product_type = ProductType.objects.filter(product_type_id=product_name).first()

                p = ProductPurchase.objects.filter(productdetails_id = productdetails_id).first()

                if p:
                    p.product_name=product_type.name,
                    p.product_type=product_type.p_type,
                    p.product = product_type
                    p.mfg_name = mfg_name
                    p.batch_no = batch_no
                    p.quantity = quantity
                    p.stock_quantity = quantity
                    p.mfg_date = mfgdate
                    p.exp_date = expdate
                    p.mrp = mrp
                    p.purchase_rate = purchaserate
                    p.purchase_date = date
                    p.save()
                
                if p is None:
                    try:
                        if len(p)>0:
                            product = ProductPurchase.objects.create(
                                user = request.user,
                                department=department,
                                product_name=product_type.name,
                                product_type=product_type.p_type,
                                product = product_type,
                                mfg_name=mfg_name,
                                batch_no=batch_no,
                                quantity=quantity,
                                stock_quantity=quantity,
                                mfg_date = mfgdate,
                                exp_date = expdate,
                                mrp = mrp, 
                                purchase_rate = purchaserate,
                                purchase_amount = amount,
                                purchase_date = date
                            )

                            purchase.products.add(product)
                    except Exception as e:
                        print(e)
            messages.success(request, 'Product Updated Successfully.')

            # Save the order
            purchase.save()
            messages.success(request, 'Update Successfully')


        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        unique_p_types = ProductType.objects.annotate(
            normalized_p_type=Trim(Upper('p_type', output_field=CharField()))
        ).values_list('normalized_p_type', flat=True).distinct()

        context = {
            'title' : 'Update Purchase',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types,
            'purchase' : purchase
        }
        return render(request, 'update_purchase.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def purchase_details_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            p = Purchase.objects.all().order_by('-order_date')
        else:
            p = Purchase.objects.filter(user=request.user).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
        elif end_date:
            p = p.filter(order_date__lt=end_date)


        d = DrugDepartment.objects.all()
        context = {
            'purchase' : p,
            'title' : f"Total Purchase : {len(p)}",
        }
        return render(request, 'purchase.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def purchase_details_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            p = Purchase.objects.all().order_by('-order_date')
        else:
            p = Purchase.objects.filter(user=request.user).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
        elif end_date:
            p = p.filter(order_date__lt=end_date)


        d = DrugDepartment.objects.all()
        context = {
            'purchase' : p,
            'title' : f"Total Purchase : {len(p)}",
        }
        return render(request, 'purchaseprint.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def purchase_delete_view(request, purchase_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':
        purchase = get_object_or_404(Purchase, purchase_id=purchase_id)
        try:
            if purchase:
                for p in purchase.products:
                    p.delete()
        except Exception as e:
            print(e)
        purchase.delete()
        return redirect('purchase_details_view')  
    else:
        logout(request)
        return redirect('signin') 




@login_required
def stock_details_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            p = ProductPurchase.objects.all().order_by('-purchase_date')
        else:
            p = ProductPurchase.objects.filter(user=request.user).order_by('-purchase_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(purchase_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(purchase_date__gte=start_datetime, purchase_date__lt=end_datetime)
        elif end_date:
            p = p.filter(purchase_date__lt=end_date)

        product_quantities = {}

        # Iterate through unique product names and aggregate their quantities
        for product_name in p.values_list('product_name', flat=True).distinct():
            total_quantity = ProductPurchase.objects.filter(product_name=product_name).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            product_quantities[product_name] = total_quantity

        d = DrugDepartment.objects.all()
        context = {
            'purchase' : p,
            'product_quantities': product_quantities,
            'title' : f"Total Purchase : {len(p)}",
        }
        return render(request, 'stock.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def stock_details_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            p = Purchase.objects.all().order_by('-order_date')
        else:
            p = Purchase.objects.filter(user=request.user).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
        elif end_date:
            p = p.filter(order_date__lt=end_date)

        product_quantities = {}

        # Iterate through unique product names and aggregate their quantities
        for product_name in p.values_list('product_name', flat=True).distinct():
            total_quantity = ProductPurchase.objects.filter(product_name=product_name).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            product_quantities[product_name] = total_quantity
        d = DrugDepartment.objects.all()
        context = {
            'purchase' : p,
            'product_quantities': product_quantities,

            'title' : f"Total Purchase : {len(p)}",
        }
        return render(request, 'stockprint.html', context=context)
    else:
        logout(request)
        return redirect('signin') 



@login_required
def supply_add_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        if request.method == 'POST':
            # Extract data from the form
            print(request.POST)
            indent = request.POST.get('indent')
            department_id = request.POST.get('department_id')
            product_name = request.POST.get('product_name')
            product_type = request.POST.get('product_type')
            mfg_name = request.POST.get('mfg_name')
            batch_no = request.POST.get('batch_no')
            date = request.POST.get('date')
            department = DrugDepartment.objects.filter(department_id=department_id).first()

            # Create a new supply instance
            supply = Supply.objects.create(
                user = request.user,
                departpment=department,
                indent  = indent,
                de = None
            )

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
                product_type_id_column = request.POST.get(f'product_type_id_column_1{i}')

                print(f"Product Type ID: {product_type_name}, MFG Name: {mfg_name}, Batch No: {batch_no}, Quantity: {quantity}")


                product_type = ProductType.objects.filter(product_type_id=product_type_id_column).first()
                print(product_type)
                p = ProductPurchase.objects.filter(productdetails_id = product_name).first()
                print(p)
                if p:
                    print(p.stock_quantity, quantity)

                    if int(p.stock_quantity) >= int(quantity):
                        p.stock_quantity = int(p.stock_quantity) -  int(quantity)
                        p.save()
                        pt = ProductType.objects.filter(product_type_id = p.product.product_type_id).first()
                        product = ProductSupply.objects.create(
                            user = request.user,
                            product = pt,
                            product_name=pt.name,
                            product_type=pt.p_type,
                            mfg_name=p.mfg_name,
                            batch_no=p.batch_no,
                            quantity=quantity,
                            mfg_date = p.mfg_date,
                            exp_date = p.exp_date,
                            stock_quantity = quantity,
                            supply_date = date
                        )

                        supply.products.add(product)

            # Save the order
            supply.save()
            messages.success(request, 'Added Successfully')

        s = Suppliar.objects.all().order_by('-created_at')
        d = DrugDepartment.objects.all().order_by('-created_at')
        p = ProductType.objects.all().order_by('-created_at')
        unique_p_types = ProductType.objects.annotate(
            normalized_p_type=Trim(Upper('p_type', output_field=CharField()))
        ).values_list('normalized_p_type', flat=True).distinct()

        context = {
            'title' : 'Add Supply',
            'suppliar' : s,
            'department' : d,
            'product' : p,
            'unique_p_types' : unique_p_types
        }
        return render(request, 'add_supply.html', context=context)
    else:
        logout(request)
        return redirect('signin') 


@login_required
def supply_delete_view(request, supply_id):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

        supply = get_object_or_404(Supply, supply_id=supply_id)
        try:
            if supply:
                for p in supply.products:
                    p.delete()
        except Exception as e:
            print(e)
        supply.delete()
        return redirect('supply_details_view')  # Replace 'success-page' with actual URL
    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_details_view(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            p = Supply.objects.filter(de = None).order_by('-order_date')
        else:
            p = Supply.objects.filter(user=request.user, de = None).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
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
        context = {
            'supply' : p,
            'title' : f"Total Supply : {len(p)}",
            'departments' : d
        }
        return render(request, 'supply.html', context=context)
    else:
        logout(request)
        return redirect('signin') 

@login_required
def supply_details_view_print(request):
    if request.user.is_superuser or request.session['user_role'] == 'Drug':

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
            p = Supply.objects.all().order_by('-order_date')
        else:
            p = Supply.objects.filter(user=request.user).order_by('-order_date')

        if start_date and end_date:
            # end_date = end_date + timedelta(days=1) 
            # start_date = start_date - timedelta(days=1)
            p = p.filter(order_date__range=(start_date, end_date))
        elif start_date:
            # If only start date is provided, include all records for that day
            next_day = start_date + timedelta(days=1)
            start_datetime = timezone.make_aware(start_date, timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_datetime = start_datetime + timedelta(days=1)

            p = p.filter(order_date__gte=start_datetime, order_date__lt=end_datetime)
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
        context = {
            'supply' : p,
            'title' : f"Total Supply : {len(p)}",
            'departments' : d
        }
        return render(request, 'supplyprint.html', context=context)

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
            date = request.POST.get('date')

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
    
