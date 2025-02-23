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

# Create your views here.

def index(request):
    context={
        "title": "Dashboard",
        "subTitle": "AI",
    }
    return render(request,"index.html", context)


def employee_list(request):
    employees = EmployeeModel.objects.all()
    context = {
        'employees': employees
    }
    return render(request, 'employees/employee-list.html', context)


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
            user.save()

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


def delete_employee(request, pk):
    employee = get_object_or_404(EmployeeModel, pk=pk)
    image_path = employee.employee_picture.path if employee.employee_picture else None

    if image_path and default_storage.exists(image_path):
        default_storage.delete(image_path)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('employee_list')


# Add Customer
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            phone = customer.customer_phone
            email = customer.customer_email
            
            # Check if phone number already exists
            if CustomerModel.objects.filter(customer_phone=phone).exists():
                messages.error(request, "Phone number is already taken!")
                return render(request, 'customers/add-customer.html', {'form': form})
            
            # Check if email already exists
            if CustomerModel.objects.filter(customer_email=email).exists():
                messages.error(request, "Email is already taken!")
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
def customer_list(request):
    customers = CustomerModel.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'customers/customer-list.html', context)

# Update Customer
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
def delete_customer(request, customer_id):
    customer = get_object_or_404(CustomerModel, id=customer_id)
    customer.delete()
    return redirect('customer_list')