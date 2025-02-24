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
    total_employees = EmployeeModel.objects.count()
    total_customers = CustomerModel.objects.count()
    total_medicine = MedicineModel.objects.count()
    total_order = OrderModel.objects.count()
    
    
    context={
        "total_employees": total_employees,
        "total_customers": total_customers,
        "total_medicine": total_medicine,
        "total_medicine_pack": 0,
        "total_order": total_order,
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

# --------Customer Functionalities
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

#---Medicine Category
def medicine_category_list(request):
    medicine_category = MedicineCategoryModel.objects.all()
    context = {
        'medicine_category':medicine_category
    }
    return render(request,'medicine_category/medicine-category-list.html',context)


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

def delete_medicine_category(request, pk):
    category = MedicineCategoryModel.objects.get(id=pk)
    category.delete()
    return redirect('medicine_category_list')


#------Medicine
def medicine_list(request):
    medicines = MedicineModel.objects.all()
    return render(request, 'medicines/medicine-list.html', {'medicines': medicines})

def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the new medicine
            medicine = form.save(commit=False)
            medicine.created_by = request.user
            medicine.save()
            messages.success(request, "Medicine added successfully!")
            return redirect('medicine_list')  # Redirect to medicine list view
        else:
            messages.error(request, "Error in form submission. Please try again.")
    else:
        form = MedicineForm()
    
    return render(request, 'medicines/add-medicine.html', {'form': form})

def update_medicine(request, pk):
    medicine = get_object_or_404(MedicineModel, pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            # Save the updated medicine
            form.save()
            messages.success(request, "Medicine updated successfully!")
            return redirect('medicine_list')  # Redirect to medicine list view
        else:
            messages.error(request, "Error in form submission. Please try again.")
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'medicines/update-medicine.html', {'form': form})

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
def medicine_stock_list(request):
    stocks = MedicineStockModel.objects.all()
    return render(request, 'medicine_stock/medicine-stock-list.html', {'stocks': stocks})

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

def delete_medicine_stock(request, pk):
    stock = get_object_or_404(MedicineStockModel, pk=pk)
    medicine = stock.medicine
    medicine.total_case_pack -= stock.total_case_pack
    medicine.save()
    stock.delete()
    messages.success(request, "Medicine stock deleted successfully!")
    return redirect('medicine_stock_list')