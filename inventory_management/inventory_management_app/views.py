from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
import random
import string
from django.db.models import Sum, Count, F
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from decimal import Decimal
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.http import HttpResponse,JsonResponse
import csv
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from weasyprint import HTML
from django.template.loader import render_to_string
import io
import os
import pandas as pd
from .decorators import user_has_access
from urllib.parse import quote
from django.core.mail import EmailMessage


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = InventoryUser.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                request.session.cycle_key()  # Regenerate the session ID for security
                return redirect('dashboard')
            else:
                messages.warning(request, "Invalid username or password.")
        except InventoryUser.DoesNotExist:
            messages.warning(request, "User does not exist.")

    return render(request, "auth/login.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if not check_password(old_password, user.password):
            messages.error(request, "Old password is incorrect.")
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('change_password')

        user.set_password(new_password)
        user.save()

        # Keep the user logged in after password change
        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully!")
        return redirect('dashboard')

    return render(request, 'auth/change-password.html')

@login_required
def dashboard(request):
    total_employees = EmployeeModel.objects.count()
    total_customers = CustomerModel.objects.count()
    
    medicine_query = MedicineModel.objects.annotate(
        total_case_pack_value=F('total_case_pack') * F('unit_price')
    ).aggregate(
        total_medicine=Count('id'),  # Counting the number of medicines directly
        total_case_pack=Sum('total_case_pack'),
        current_product_value=Sum('total_case_pack_value')
    )
    medicine_data = MedicineModel.objects.all()[:6]

    billing_query = BillingModel.objects.annotate(
        total_sale_amount_value=F('total_amount')
    ).aggregate(
        total_billing=Count('id'),
        total_sale_amount=Sum('total_sale_amount_value'),
        
    )
    
    total_purchase_amount = MedicineStockModel.objects.aggregate(total_amount=Sum('total_amount'))
    total_wastage_quantity = BottleBreakageModel.objects.aggregate(total_wastage_quantity=Sum('lost_quantity'))

    thirty_days_ago = now().date() - timedelta(days=30)
    
    latest_billing= BillingModel.objects.all().order_by('-id')[:5]
    latest_stock = MedicineStockModel.objects.all().order_by('-id')[:5]
    
    billings = (
        BillingModel.objects
        .filter(billing_date__date__gte=thirty_days_ago) 
        .annotate(billing_date_only=TruncDate('billing_date'))
        .values('billing_date_only')
        .annotate(total_amount=Sum('total_amount'))
        .order_by('billing_date_only')
    )

    # Convert data for ApexCharts
    billing_chart_data = {
        "dates": [billing['billing_date_only'].strftime('%Y-%m-%d') for billing in billings],
        "totals": [float(billing['total_amount']) for billing in billings]
    }

    context = {
        "total_employees": total_employees,
        "total_customers": total_customers,
        "total_billing": billing_query['total_billing'],
        "total_medicine": medicine_query['total_medicine'],
        "total_medicine_pack": medicine_query['total_case_pack'] or 0,
        "current_product_value": medicine_query['current_product_value'] or 0,
        "total_purchase_amount": total_purchase_amount['total_amount'] or 0,
        "total_sale_amount": billing_query['total_sale_amount'] or 0,
        "total_wastage_quantity": total_wastage_quantity['total_wastage_quantity'] or 0,
        "total_revenue_amount": 0,
        "billing_chart_data": billing_chart_data,  
        "latest_billing":latest_billing,
        "latest_stock":latest_stock,
        "medicine_data":medicine_data,
    }

    return render(request, "index.html", context)

@login_required
@user_has_access('employee_view','employee_management')
def employee_list(request):
    employees = EmployeeModel.objects.all()
    context = {
        'employees': employees
    }
    return render(request, 'employees/employee-list.html', context)

@user_has_access('employee_management')
@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            user_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            username = f"EID-{random.randint(100000, 999999)}"

            while InventoryUser.objects.filter(username=username).exists():
                username = f"EID-{random.randint(100000, 999999)}"

            user = InventoryUser.objects.create(
                username=username,
                email=form.cleaned_data['email'],
                role=form.cleaned_data['role'],
            )
            user.set_password(user_password)
            
            # If role is 'Admin', store predefined access list
            if user.role == 'Admin':
                user_access_list = ['employee_management', 'employee_view', 'customer_management', 'customer_view', 'product_management', 'product_view', 'low_stocks', 'billing_management', 'inventory_report', 'wastage_report', 'billing_report']

            else:
                user_access_list = form.cleaned_data['user_access_list']

            user.user_access_list = ','.join(user_access_list)
            
            user.save()

            employee.employee_id = username
            employee.created_by = request.user
            employee.employee_user = user
            employee.save()

            send_mail(
                subject="Account Login Info",
                message=f"Your Account successfully created. Username: {username}, Password: {user_password}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            messages.success(request, "Employee added successfully!")
            return redirect('employee_list')
    else:
        form = EmployeeForm()

    return render(request, 'employees/add-employee.html', {'form': form})


@user_has_access('employee_management')
@login_required
def update_employee(request, pk):
    employee = get_object_or_404(EmployeeModel, pk=pk)
    old_image_path = employee.employee_picture.path if employee.employee_picture else None
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            if 'employee_picture' in request.FILES and old_image_path:
                if default_storage.exists(old_image_path):
                    default_storage.delete(old_image_path)
            form.save()
            messages.success(request, "Employee updated successfully!")
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/update-employee.html', {'form': form})

@login_required
@user_has_access('employee_management')
def delete_employee(request, pk):
    employee = get_object_or_404(EmployeeModel, pk=pk)
    image_path = employee.employee_picture.path if employee.employee_picture else None

    if image_path and default_storage.exists(image_path):
        default_storage.delete(image_path)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('employee_list')

# --------Customer Functionalities
@login_required
@user_has_access('customer_management','billing_management')
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            phone = customer.customer_phone
            email = customer.customer_email
            
            # Check if phone number already exists
            if CustomerModel.objects.filter(customer_phone=phone).exists():
                messages.warning(request, "Phone number is already taken!")
                return render(request, 'customers/add-customer.html', {'form': form})
            
            # Check if email already exists
            if CustomerModel.objects.filter(customer_email=email).exists():
                messages.warning(request, "Email is already taken!")
                return render(request, 'customers/add-customer.html', {'form': form})

            # If no errors, save the customer
            customer.created_by = request.user
            customer.save()
            messages.success(request, "Customer added successfully!")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'customers/add-customer.html', {'form': form})


# List Customers
@login_required
@user_has_access('customer_management','customer_view','billing_management')
def customer_list(request):
    customers = CustomerModel.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'customers/customer-list.html', context)

# Update Customer
@login_required
@user_has_access('customer_management','billing_management')
def update_customer(request, customer_id):
    customer = get_object_or_404(CustomerModel, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
        
    context = {
        'form':form,
    }
    
    return render(request, 'customers/update-customer.html', context)

# Delete Customer
@login_required
@user_has_access('customer_management','billing_management')
def delete_customer(request, customer_id):
    customer = get_object_or_404(CustomerModel, id=customer_id)
    customer.delete()
    return redirect('customer_list')

#---Medicine Category
@login_required
@user_has_access('product_management')
def medicine_category_list(request):
    medicine_category = MedicineCategoryModel.objects.all()
    context = {
        'medicine_category':medicine_category
    }
    return render(request,'medicine_category/medicine-category-list.html',context)


@login_required
@user_has_access('product_management')
def add_medicine_category(request):
    if request.method == 'POST':
        form = MedicineCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medicine_category_list')
    else:
        form = MedicineCategoryForm()
    context = {
        'form':form
    }
    return render(request,'medicine_category/add-medicine-category.html',context)

@login_required
@user_has_access('product_management')
def update_medicine_category(request,pk):
    category = MedicineCategoryModel.objects.get(id=pk)
    if request.method == 'POST':
        form = MedicineCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('medicine_category_list')
    else:
        form = MedicineCategoryForm(instance=category)
    context = {
        'form':form
    }
    return render(request,'medicine_category/update-medicine-category.html',context)

@login_required
@user_has_access('product_management')
def delete_medicine_category(request, pk):
    category = MedicineCategoryModel.objects.get(id=pk)
    category.delete()
    return redirect('medicine_category_list')

#---Medicine Unit
@login_required
@user_has_access('product_management')
def medicine_unit_list(request):
    medicine_unit = MedicineUnitModel.objects.all()
    context = {
        'medicine_unit':medicine_unit
    }
    return render(request,'medicine_unit/medicine-unit-list.html',context)

@login_required
@user_has_access('product_management')
def add_medicine_unit(request):
    if request.method == 'POST':
        form = MedicineUnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Unit added successfully!")
            return redirect('medicine_unit_list')
    else:
        form = MedicineUnitForm()
    context = {
        'form':form
    }
    return render(request,'medicine_unit/add-medicine-unit.html',context)

@login_required
@user_has_access('product_management')
def update_medicine_unit(request,pk):
    unit = MedicineUnitModel.objects.get(id=pk)
    if request.method == 'POST':
        form = MedicineUnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, "Unit updated successfully!")
            return redirect('medicine_unit_list')
    else:
        form = MedicineUnitForm(instance=unit)
    context = {
        'form':form
    }
    return render(request,'medicine_unit/update-medicine-unit.html',context)

@login_required
@user_has_access('product_management')
def delete_medicine_unit(request, pk):
    unit = MedicineUnitModel.objects.get(id=pk)
    unit.delete()
    messages.success(request, "Unit deleted successfully!")
    return redirect('medicine_unit_list')


#------Medicine
@login_required
@user_has_access('product_management','product_view','low_stocks','billing_management')
def medicine_list(request):
    medicines = MedicineModel.objects.all().order_by('-id')
    return render(request, 'medicines/medicine-list.html', {'medicines': medicines})

def sku_generate():
    return f"MED{random.randint(10000, 99999)}"

@login_required
@user_has_access('product_management')
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.created_by = request.user
            while True:
                sku_no = sku_generate()
                if not MedicineModel.objects.filter(sku=sku_no).exists():
                    break
            
            medicine.sku = sku_no
            # Remove extra spaces from each part
            medicine_name = " ".join(medicine.medicine_name.split())  # Removes multiple spaces
            pack_units = " ".join(medicine.pack_units.unit_name.split())
            pack_size = str(medicine.pack_size).strip()
            
            # Construct the final name
            full_medicine_name = f"{medicine_name} {pack_size} {pack_units}"

            # Case-insensitive check without modifying actual stored name
            if MedicineModel.objects.filter(medicine_name__iexact=full_medicine_name).exists():
                messages.error(request, "This medicine already exists!")
            else:
                medicine.medicine_name = full_medicine_name
                medicine.save()
                messages.success(request, "Medicine added successfully!")
                return redirect('medicine_list')
        else:
            messages.warning(request, "Error in form submission. Please try again.")
    else:
        form = MedicineForm()
    
    return render(request, 'medicines/add-medicine.html', {'form': form})

@login_required
@user_has_access('product_management')
def update_medicine(request, pk):
    medicine = get_object_or_404(MedicineModel, pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():

            form.save()
            messages.success(request, "Medicine updated successfully!")
            return redirect('medicine_list')  
        else:
            messages.warning(request, "Error in form submission. Please try again.")
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'medicines/update-medicine.html', {'form': form})

@login_required
@user_has_access('product_management')
def delete_medicine(request, pk):
    medicine = get_object_or_404(MedicineModel, pk=pk)
    
    # Delete the medicine and its associated image
    if medicine.medicine_picture:
        try:
            medicine.medicine_picture.delete()
        except Exception as e:
            pass
    
    medicine.delete()
    messages.success(request, "Medicine deleted successfully!")
    return redirect('medicine_list')

#--------Medicine Stock
@login_required
@user_has_access('product_management')
def medicine_stock_list(request):
    stocks = MedicineStockModel.objects.all()
    return render(request, 'medicine_stock/medicine-stock-list.html', {'stocks': stocks})

@login_required
@user_has_access('product_management')
def add_medicine_stock(request):
    if request.method == "POST":
        form = MedicineStockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_by = request.user
            stock.save()
            
            # Update medicine stock
            medicine = stock.medicine
            medicine.total_case_pack += stock.total_case_pack
            medicine.save()
            
            messages.success(request, "Medicine stock added successfully!")
            return redirect('medicine_stock_list')
    else:
        form = MedicineStockForm()
    return render(request, 'medicine_stock/add-medicine-stock.html', {'form': form})

@login_required
@user_has_access('product_management')
def update_medicine_stock(request, pk):
    stock = get_object_or_404(MedicineStockModel, pk=pk)
    old_total_case_pack = stock.total_case_pack

    if request.method == "POST":
        form = MedicineStockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            
            # Adjust the medicine stock
            medicine = stock.medicine
            medicine.total_case_pack += (stock.total_case_pack - old_total_case_pack)
            medicine.save()
            
            messages.success(request, "Medicine stock updated successfully!")
            return redirect('medicine_stock_list')
    else:
        form = MedicineStockForm(instance=stock)
    return render(request, 'medicine_stock/update-medicine-stock.html', {'form': form})

@login_required
@user_has_access('product_management')
def delete_medicine_stock(request, pk):
    stock = get_object_or_404(MedicineStockModel, pk=pk)
    medicine = stock.medicine
    medicine.total_case_pack -= stock.total_case_pack
    medicine.save()
    stock.delete()
    messages.success(request, "Medicine stock deleted successfully!")
    return redirect('medicine_stock_list')

#------Low stock
@login_required
@user_has_access('product_management','low_stocks','billing_management')
def low_stocks(request):
    low_stock_data = MedicineModel.objects.filter(total_case_pack__lt=10).values('id', 'medicine_name', 'pack_size','total_case_pack','unit_price', 'stocks')
    context = {
        'low_stock_data':low_stock_data,
    }
    return render(request,'medicine_stock/low-stock.html',context)    


#--------Bottle Breakage
@login_required
@user_has_access('product_management')
def add_bottle_breakage(request):
    if request.method == "POST":
        form = BottleBreakageForm(request.POST)
        if form.is_valid():
            bottle_breakage = form.save(commit=False)
            bottle_breakage.created_by = request.user
            
            medicine = bottle_breakage.medicine
            
            if medicine:
                try:
                    medicine_stock = MedicineModel.objects.get(id=medicine.id)
                    if medicine_stock.total_case_pack < bottle_breakage.lost_quantity:
                        messages.warning(request, f"Invalid Lost Quantity! Available stock: {medicine_stock.total_case_pack} case pack")
                        return redirect('add_bottle_breakage')
                    else:
                        medicine_stock.total_case_pack -= bottle_breakage.lost_quantity
                        medicine_stock.save()
                except MedicineModel.DoesNotExist:
                    messages.warning(request, "Medicine data not found.")
                    return redirect('add_bottle_breakage')
            
            bottle_breakage.save()
            messages.success(request, "Bottle breakage recorded successfully.")
            return redirect('bottle_breakage_list')
    else:
        form = BottleBreakageForm()
    
    return render(request, "bottle_breakage/add-bottle-breakage.html", {"form": form})

# Update Bottle Breakage Entry
@login_required
@user_has_access('product_management')
def update_bottle_breakage(request, pk):
    bottle_breakage = get_object_or_404(BottleBreakageModel, pk=pk)
    previous_lost_quantity = bottle_breakage.lost_quantity
    
    if request.method == "POST":
        form = BottleBreakageForm(request.POST, instance=bottle_breakage)
        if form.is_valid():
            updated_breakage = form.save(commit=False)
            medicine = updated_breakage.medicine
            
            if medicine:
                try:
                    medicine_stock = MedicineModel.objects.get(id=medicine.id)
                    medicine_stock.total_case_pack += previous_lost_quantity  # Revert previous deduction
                    
                    if medicine_stock.total_case_pack < updated_breakage.lost_quantity:
                        messages.warning(request, f"Invalid Lost Quantity! Available stock: {medicine_stock.total_case_pack} case pack")
                        return redirect('update_bottle_breakage', pk=pk)
                    else:
                        medicine_stock.total_case_pack -= updated_breakage.lost_quantity
                        medicine_stock.save()
                except MedicineModel.DoesNotExist:
                    messages.warning(request, "Medicine data not found.")
                    return redirect('update_bottle_breakage', pk=pk)
            
            updated_breakage.save()
            messages.success(request, "Bottle breakage updated successfully.")
            return redirect('bottle_breakage_list')
    else:
        form = BottleBreakageForm(instance=bottle_breakage)
    
    return render(request, "bottle_breakage/update-bottle-breakage.html", {"form": form})


@login_required
@user_has_access('product_management')
def delete_bottle_breakage(request, pk):
    bottle_breakage = get_object_or_404(BottleBreakageModel, pk=pk)
    medicine = bottle_breakage.medicine
    
    if medicine:
        try:
            medicine_stock = MedicineModel.objects.get(id=medicine.id)
            medicine_stock.total_case_pack += bottle_breakage.lost_quantity  # Restore stock
            medicine_stock.save()
        except MedicineModel.DoesNotExist:
            messages.warning(request, "Medicine data not found.")
            return redirect('bottle_breakage_list')
    
    bottle_breakage.delete()
    messages.success(request, "Bottle breakage record deleted successfully.")
    return redirect('bottle_breakage_list')

# List Bottle Breakages
@login_required
@user_has_access('product_management')
def bottle_breakage_list(request):
    bottle_breakages = BottleBreakageModel.objects.all()
    return render(request, "bottle_breakage/bottle-breakage-list.html", {"bottle_breakages": bottle_breakages})


#---------Billing Functionalities
def billing_generate():
    return f"ORD-{random.randint(100000, 999999)}"

@login_required
@user_has_access('billing_management')
def billing_list(request):
    billing_status_filter = request.GET.get('status', 'All')
    
    if billing_status_filter == 'All':
        billings = BillingModel.objects.annotate(
            total_items=Count('billing_items'), 
            total_price=Sum('billing_items__total_price'),
            total_medicine_quantity=Sum('billing_items__medicine_quantity')  
        )
    else:
        billings = BillingModel.objects.filter(billing_status=billing_status_filter).annotate(
            total_items=Count('billing_items'),
            total_price=Sum('billing_items__total_price'),
            total_medicine_quantity=Sum('billing_items__medicine_quantity')
        )

    return render(request, 'billings/billing-list.html', {'billings': billings, 'billing_status_filter': billing_status_filter})

@login_required
@user_has_access('billing_management')
def billing_create(request):
    medicines = MedicineModel.objects.all()  # Fetch all medicines
    
    if request.method == "POST":
        billing_form = BillingForm(request.POST)
        
        if billing_form.is_valid():
            billing = billing_form.save(commit=False)
            
            if billing.customer_user is None:
                # If no customer is selected, create a new customer
                name = billing_form.cleaned_data['customer_name']
                phone = billing_form.cleaned_data['customer_phone']
                email = billing_form.cleaned_data['customer_email']
                dob = billing_form.cleaned_data['customer_dob']
                address = billing_form.cleaned_data['customer_address']
                
                # Check if phone number already exists
                if CustomerModel.objects.filter(customer_phone=phone).exists():
                    messages.warning(request, "Phone number is already taken!")
                    return render(request, 'billings/add-billing.html', {'billing_form': billing_form, 'medicines': medicines})
                
                # Check if email already exists
                if CustomerModel.objects.filter(customer_email=email).exists():
                    messages.warning(request, "Email is already taken!")
                    return render(request, 'billings/add-billing.html', {'billing_form': billing_form, 'medicines': medicines})

                # Create a new customer
                customer = CustomerModel.objects.create(
                    customer_name=name,
                    customer_phone=phone,
                    customer_email=email,
                    customer_dob=dob,
                    customer_address=address,
                    created_by=request.user,
                )
                billing.customer_user = customer  # Assign the newly created customer to the billing

            # Generate unique billing number
            while True:
                billing_no = billing_generate()
                if not BillingModel.objects.filter(billing_no=billing_no).exists():
                    break

            billing.billing_no = billing_no
            billing.created_by = request.user
            billing.total_amount = Decimal(0)
            billing.save()

            # Processing multiple billing items
            medicines_ids = request.POST.getlist('medicine[]')
            quantities = request.POST.getlist('medicine_quantity[]')

            for i in range(len(medicines_ids)):
                try:
                    medicine = MedicineModel.objects.get(id=medicines_ids[i])
                    medicine_quantity = int(quantities[i])

                    if medicine_quantity > medicine.total_case_pack:
                        messages.warning(request, f"Stock not available for {medicine.medicine_name}")
                        billing.delete()
                        return redirect('billing_create')

                    unit_price = Decimal(medicine.unit_price)
                    total_price = medicine_quantity * unit_price

                    BillingItemModel.objects.create(
                        billing=billing,
                        medicine=medicine,
                        medicine_quantity=medicine_quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    # Deduct stock
                    medicine.total_case_pack -= medicine_quantity
                    medicine.save()

                    billing.total_amount += total_price

                except MedicineModel.DoesNotExist:
                    messages.warning(request, "Invalid medicine selection.")
                    billing.delete()
                    return redirect('billing_create')

            billing.tax_percentage = Decimal('18')
            billing.tax_amount = billing.total_amount * (billing.tax_percentage / Decimal('100'))
            billing.discount_amount = billing.total_amount * (billing.discount_percentage / Decimal('100'))
            billing.total_amount += billing.tax_amount - billing.discount_amount
            billing.save()
            generate_invoice(request, billing.id)

            messages.success(request, "Billing created successfully!")
            return redirect('invoice', billing.id)

    else:
        billing_form = BillingForm()
    
    context = {
        'billing_form': billing_form,
        'medicines': medicines,
    }

    return render(request, 'billings/add-billing.html', context)

def get_customer_details(request, customer_id):
    # Fetch the customer object
    customer = get_object_or_404(CustomerModel, id=customer_id)
    
    # Return customer details as JSON
    data = {
        'customer_name': customer.customer_name,
        'customer_phone': customer.customer_phone,
        'customer_email': customer.customer_email,
        'customer_dob': customer.customer_dob.strftime('%Y-%m-%d'),
        'customer_address': customer.customer_address,
    }
    return JsonResponse(data)

@login_required
@user_has_access('billing_management')
def billing_update(request, pk):
    billing = get_object_or_404(BillingModel, id=pk)  # Get the billing to be updated
    medicines = MedicineModel.objects.all()  # Fetch all medicines
    
    if request.method == "POST":
        billing_form = BillingForm(request.POST, instance=billing)

        if billing_form.is_valid():
            updated_billing= billing_form.save(commit=False)

            # Update billing total amount
            updated_billing.total_amount = Decimal(0)
            updated_billing.save()

            # Processing multiple billing items
            medicines_ids = request.POST.getlist('medicine')
            quantities = request.POST.getlist('medicine_quantity')

            # First, remove old billing items (if any)
            billing_items = billing.billing_items.all() 
            for item in billing_items:
                item.medicine.total_case_pack += item.medicine_quantity 
                item.medicine.save()
                item.delete()

            # Adding new billing items
            for i in range(len(medicines_ids)):
                try:
                    medicine = MedicineModel.objects.get(id=medicines_ids[i])
                    medicine_quantity = int(quantities[i])

                    if medicine_quantity > medicine.total_case_pack:
                        messages.warning(request, f"Stock not available for {medicine.medicine_name}")
                        return redirect('billing_update', billing_id=billing.id)

                    unit_price = Decimal(medicine.unit_price)
                    total_price = medicine_quantity * unit_price

                    BillingItemModel.objects.create(
                        billing=updated_billing,
                        medicine=medicine,
                        medicine_quantity=medicine_quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    # Deduct stock
                    medicine.total_case_pack -= medicine_quantity
                    medicine.save()

                    updated_billing.total_amount += total_price

                except MedicineModel.DoesNotExist:
                    messages.warning(request, "Invalid medicine selection.")
                    return redirect('billing_update', billing_id=billing.id)
            
            updated_billing.tax_amount = updated_billing.total_amount * (updated_billing.tax_percentage / Decimal('100'))
            updated_billing.discount_amount = updated_billing.total_amount * (updated_billing.discount_percentage / Decimal('100'))
            
            updated_billing.total_amount += updated_billing.tax_amount - updated_billing.discount_amount
            updated_billing.save()

            messages.success(request, "Billing updated successfully!")
            return redirect('billing_list')

    else:
        billing_form = BillingForm(instance=billing)

    return render(request, 'billings/update-billing.html', {
        'billing_form': billing_form, 
        'medicines': medicines, 
        'billing': billing,
        'billing_items': billing.billing_items.all()  # Fixed here to access related billing items
    })

@login_required
@user_has_access('billing_management')
def billing_delete(request, pk):
    billing = get_object_or_404(BillingModel, pk=pk)

    for billing_item in billing.billing_items.all():
        medicine = billing_item.medicine
        medicine.total_case_pack += billing_item.medicine_quantity
        medicine.save()

    billing.delete()
    messages.success(request, "Billing deleted successfully!")
    return redirect('billing_list')

@login_required
@user_has_access('billing_management')
def invoice_list(request):
    billings = BillingModel.objects.annotate(
        total_items=Count('billing_items'),
        total_price=Sum('billing_items__total_price'),  
        total_medicine_quantity=Sum('billing_items__medicine_quantity')  
    )
    
    return render(request, 'invoices/invoice-list.html', {'billings': billings})

@login_required
@user_has_access('billing_management')
def invoice(request, billing_id):
    # Fetch the billing with the given billing_id and related billing items
    billing = get_object_or_404(BillingModel, id=billing_id)
    billing_items = BillingItemModel.objects.filter(billing=billing)
    subtotal = sum(item.total_price for item in billing_items)

    # Pass the billing and billing items to the template
    context = {
        'billing': billing,
        'billing_items': billing_items,
        'subtotal': subtotal,
    }
    return render(request, 'invoices/invoice.html', context)


def generate_invoice(request, billing_id):
    invoice = BillingModel.objects.get(id=billing_id)
    billing_items = BillingItemModel.objects.filter(billing=invoice)
    subtotal = sum(item.total_price for item in billing_items)

    context = {
        'billing': invoice,
        'billing_items': billing_items,
        'subtotal': subtotal,
    }
    html_string = render_to_string('invoices/invoice_template.html',context)

    pdf = HTML(string=html_string).write_pdf()

    invoice_folder = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoice_folder, exist_ok=True)

    # Define the file path
    file_path = os.path.join(invoice_folder, f'invoice_{invoice.billing_no}.pdf')

    # Save the PDF to the file
    with open(file_path, 'wb') as f:
        f.write(pdf)

    # Optionally store the file path in the database (optional)
    invoice.pdf_file = os.path.join('invoices', f'invoice_{invoice.billing_no}.pdf')
    invoice.save()

    # Return the PDF in the response without triggering a download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=invoice_{invoice.billing_no}.pdf'  # This opens the PDF in the browser

    return response

@login_required
@user_has_access('product_management','inventory_report')
def inventory_report(request):
    # Query the MedicineModel with the related stock and sales data
    inventory_report = MedicineModel.objects.annotate(
        total_stock=Sum('medicinestocks__total_case_pack'),
        total_sales=Sum('medicine_billings__medicine_quantity'),
        total_loss=Sum('breakages__lost_quantity')
    ).values(
        'medicine_name', 
        'total_stock', 
        'total_sales', 
        'total_loss', 
        'unit_price'
    )

    # For downloading the report in CSV format
    if request.GET.get('download') == 'true':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
        writer = csv.writer(response)

        # Write headers to CSV file
        writer.writerow(['Medicine Name', 'Total Stock', 'Total Sales', 'Total Loss', 'Unit Price'])

        # Write data to CSV file
        for item in inventory_report:
            writer.writerow([item['medicine_name'], item['total_stock'], item['total_sales'], item['total_loss'], item['unit_price']])

        return response

    return render(request, 'reports/inventory-report.html', {'inventory_report': inventory_report})

@login_required
@user_has_access('product_management','wastage_report')
def wastage_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_employee_id = request.GET.get('employee_id')
    selected_medicine_id = request.GET.get('medicine_name')

    # Default query to fetch BottleBreakageModel objects with filtering logic
    wastage_report = BottleBreakageModel.objects.select_related(
        'medicine', 
        'responsible_employee', 
    ).values(
        'medicine__medicine_name', 
        'lost_quantity', 
        'responsible_employee__employee_user__username',
        'date_time',
        'id',
    )

    # Apply date filter if both start_date and end_date are provided
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            wastage_report = wastage_report.filter(date_time__range=[start_date, end_date])
        except ValueError:
            wastage_report = wastage_report.none()

    # Apply employee filter if selected
    if selected_employee_id:
        wastage_report = wastage_report.filter(responsible_employee__id=selected_employee_id)

    # Apply medicine filter if selected
    if selected_medicine_id:
        wastage_report = wastage_report.filter(medicine__id=selected_medicine_id)

    # Fetch employees and medicines used in BottleBreakageModel to pass to the template
    employees = BottleBreakageModel.objects.values('responsible_employee__id', 'responsible_employee__employee_user__username').distinct()
    medicines = BottleBreakageModel.objects.values('medicine__id', 'medicine__medicine_name').distinct()

    # Export to CSV functionality
    if request.GET.get('download') == 'true':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="wastage_report.csv"'
        writer = csv.writer(response)

        # Write headers to CSV file
        writer.writerow(['Medicine Name', 'Lost Quantity', 'Responsible Employee', 'Date'])

        # Write data to CSV file
        for item in wastage_report:
            writer.writerow([item['medicine__medicine_name'], item['lost_quantity'], item['responsible_employee__employee_user__username'], item['date_time']])

        return response

    return render(request, 'reports/wastage-report.html', {
        'wastage_report': wastage_report,
        'start_date': start_date,
        'end_date': end_date,
        'employees': employees,
        'medicines': medicines,
        'selected_employee_id': selected_employee_id,
        'selected_medicine_id': selected_medicine_id,
    })


@login_required  
@user_has_access('billing_report','billing_management')
def billing_trends_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    billing_trends = BillingItemModel.objects.annotate(
        medicine_name=F('medicine__medicine_name'),
        billing_date=F('billing__billing_date'), 
        total_sales=F('medicine_quantity'),
        total_revenue=F('total_price'),
    ).values(
        'medicine_name',
        'billing_date',
        'total_sales',
        'total_revenue',
    ).order_by('-billing_date')

    # Filter by date range if provided
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Extend end_date to include the entire day
            end_datetime = datetime.combine(end_date, datetime.max.time())

            billing_trends = billing_trends.filter(billing__billing_date__range=[start_date, end_datetime])
        except ValueError:
            # Handle invalid date format
            billing_trends = billing_trends.none()

    # For CSV download
    if request.GET.get('download') == 'true':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="billing_trends_report.csv"'
        writer = csv.writer(response)

        # Write headers to CSV file
        writer.writerow(['Medicine Name', 'Total Qty', 'Total Revenue','Timestamp'])

        # Write data to CSV file
        for item in billing_trends:
            writer.writerow([item['medicine_name'], item['total_sales'], item['total_revenue'], item['billing_date']])

        return response

    return render(request, 'reports/billing-trends-report.html', {
        'billing_trends': billing_trends,
        'start_date': start_date,
        'end_date': end_date,
    })
    


#-----Medicine Upload to Excel
@login_required
@user_has_access('product_management')
def upload_medicine(request):
    if request.method == "POST":
        try:
            # Step 1: Read the uploaded file
            excel_file = request.FILES["file"]
            file_name = excel_file.name

            if file_name.endswith(".csv"):
                df = pd.read_csv(excel_file)
            elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
                df = pd.read_excel(excel_file, engine="openpyxl")
            else:
                return JsonResponse({"message": "Unsupported file format! Please upload CSV or Excel."}, status=400)

            # Step 2: Validate columns
            df.columns = df.columns.str.strip().str.lower()
            required_columns = {"medicine_name", "medicine_category", "medicine_type", "pack_units", "description", "pack_size", "unit_price"}
            
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                return JsonResponse({"message": f"Missing columns: {', '.join(list(missing_columns))}"}, status=400)

            # Step 3: Process rows
            valid_rows = []
            invalid_rows = []
            medicine_types = dict(MedicineModel.MEDICINE_TYPES)
            valid_flag = False

            for _, row in df.iterrows():
                row_dict = row.to_dict()
                errors = []

                # Validate medicine name
                if pd.isna(row["medicine_name"]) or row["medicine_name"].strip() == "":
                    errors.append("Missing medicine name")
                
                # Validate medicine category
                try:
                    category = MedicineCategoryModel.objects.get(category_name=row["medicine_category"])
                except MedicineCategoryModel.DoesNotExist:
                    errors.append(f"Invalid category: {row['medicine_category']}")

                try:
                    unit = MedicineUnitModel.objects.get(unit_name=row["pack_units"])
                    while True:
                        sku_no = sku_generate()
                        if not MedicineModel.objects.filter(sku=sku_no).exists():
                            break

                    created_by = request.user
                    # Move full_medicine_name assignment outside the try block
                    full_medicine_name = f"{row['medicine_name']} {row['pack_size']} {unit}"
                    print("medicine name: ", full_medicine_name)
                    
                except MedicineUnitModel.DoesNotExist:
                    errors.append(f"Invalid pack unit: {row['pack_units']}")
                    full_medicine_name = None  # Ensure it is defined even if the unit doesn't exist

                # Now, proceed with the rest of the code
                if row["medicine_name"] and full_medicine_name:
                    if MedicineModel.objects.filter(medicine_name=full_medicine_name).exists():
                        continue

                # Validate medicine type
                if row["medicine_type"] not in medicine_types:
                    errors.append(f"Invalid medicine type: {row['medicine_type']}")

                # Add to valid or invalid rows
                if errors:
                    row_dict["error_reason"] = "; ".join(errors)
                    invalid_rows.append(row_dict)
                else:
                    valid_rows.append(MedicineModel(
                        sku=sku_no,
                        medicine_name=full_medicine_name,
                        medicine_category=category,
                        medicine_type=row["medicine_type"],
                        pack_units=unit,
                        description=row["description"],
                        pack_size=row["pack_size"],
                        unit_price=row["unit_price"],
                        created_by=created_by,
                    ))

            # Step 4: Save valid rows
            if valid_rows:
                valid_flag = True
                MedicineModel.objects.bulk_create(valid_rows)

            # Step 5: Handle invalid rows
            if invalid_rows:
                error_df = pd.DataFrame(invalid_rows)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    error_df.to_excel(writer, index=False)

                output.seek(0)
                
                if valid_flag:
                    messages.warning(request, "Data imported successfully! But some data had errors. Please review the error file.")
                else:
                    messages.error(request, "No valid data found. Please check the downloaded error file.")

                # Return Excel file for invalid rows
                response = HttpResponse(
                    output.getvalue(),  # Use getvalue() to get the binary data
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response["Content-Disposition"] = 'attachment; filename="error_data.xlsx"'
                return response

            # Step 6: Return success response if no invalid rows
            return JsonResponse({"message": "Data imported successfully!"})

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({"message": f"Error importing data: {str(e)}"}, status=500)

    # Handle invalid request method
    return JsonResponse({"message": "Invalid request method."}, status=400)

def send_invoice_email(request, billing_id):
    billing = get_object_or_404(BillingModel, id=billing_id)
    
    subject = "Your Billing Invoice"
    message = "Dear Customer, Please find attached your invoice."

    to_email = billing.customer_email
    
    from_email = settings.EMAIL_HOST_USER
    email = EmailMessage(subject, message, from_email, [to_email])

    if billing.pdf_file:
        with open(billing.pdf_file.path, 'rb') as pdf:
            email.attach('invoice.pdf', pdf.read(), 'application/pdf')

        email.send()
        messages.success(request, "Invoice sent successfully to the customer.")
    else:
        messages.error(request, "Invoice file not found.")
    return redirect('invoice_list') 


def send_invoice_via_whatsapp(request, billing_id):
    billing = get_object_or_404(BillingModel, id=billing_id)

    if not billing.pdf_file:
        return HttpResponse("Invoice PDF not available", status=404)

    # Ensure the phone number has the correct country code
    customer_phone = billing.customer_phone
    if not customer_phone.startswith("+"):
        customer_phone = f"+88{customer_phone}"  # Adjust based on your country

    pdf_file_url = f'http://inventory.mrshakil.com{billing.pdf_file.url}'

    # Encode the message properly
    message = f"Hi, please find my invoice here: {pdf_file_url}"
    encoded_message = quote(message)  # Encode special characters properly

    # Construct the WhatsApp URL
    whatsapp_url = f"https://wa.me/{customer_phone}?text={encoded_message}"

    return redirect(whatsapp_url)