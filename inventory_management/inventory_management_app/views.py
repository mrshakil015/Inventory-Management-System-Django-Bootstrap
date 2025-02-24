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
from django.db.models import Sum, Count
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.contrib.auth.forms import AuthenticationForm


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = InventoryUser.objects.get(username=username)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        
        except InventoryUser.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, "auth/login.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
def dashboard(request):
    total_employees = EmployeeModel.objects.count()
    total_customers = CustomerModel.objects.count()
    total_medicine = MedicineModel.objects.count()
    total_order = OrderModel.objects.count()
    total_medicine_pack = MedicineModel.objects.aggregate(
        total_case_pack=Sum('total_case_pack')
    )
    
    total_purchase_amount = MedicineStockModel.objects.aggregate(
        total_amount=Sum('total_amount')
    )
    total_sale_amount = OrderModel.objects.aggregate(
        total_amount=Sum('total_amount')
    )

    
    context={
        "total_employees": total_employees,
        "total_customers": total_customers,
        "total_medicine": total_medicine,
        "total_order": total_order,
        "total_medicine_pack": total_medicine_pack['total_case_pack'] or 0,
        "total_purchase_amount": total_purchase_amount['total_amount'] or 0,
        "total_sale_amount": total_sale_amount['total_amount'] or 0,
        "total_revenue_amount": 0,
        
    }
    return render(request,"index.html", context)

@login_required
def employee_list(request):
    employees = EmployeeModel.objects.all()
    context = {
        'employees': employees
    }
    return render(request, 'employees/employee-list.html', context)

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
def customer_list(request):
    customers = CustomerModel.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'customers/customer-list.html', context)

# Update Customer
@login_required
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
def delete_customer(request, customer_id):
    customer = get_object_or_404(CustomerModel, id=customer_id)
    customer.delete()
    return redirect('customer_list')

#---Medicine Category
@login_required
def medicine_category_list(request):
    medicine_category = MedicineCategoryModel.objects.all()
    context = {
        'medicine_category':medicine_category
    }
    return render(request,'medicine_category/medicine-category-list.html',context)


@login_required
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
def delete_medicine_category(request, pk):
    category = MedicineCategoryModel.objects.get(id=pk)
    category.delete()
    return redirect('medicine_category_list')


#------Medicine
@login_required
def medicine_list(request):
    medicines = MedicineModel.objects.all()
    return render(request, 'medicines/medicine-list.html', {'medicines': medicines})

@login_required
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
            messages.warning(request, "Error in form submission. Please try again.")
    else:
        form = MedicineForm()
    
    return render(request, 'medicines/add-medicine.html', {'form': form})

@login_required
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
            messages.warning(request, "Error in form submission. Please try again.")
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'medicines/update-medicine.html', {'form': form})

@login_required
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
def medicine_stock_list(request):
    stocks = MedicineStockModel.objects.all()
    return render(request, 'medicine_stock/medicine-stock-list.html', {'stocks': stocks})

@login_required
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
def low_stocks(request):
    low_stock_data = MedicineModel.objects.filter(total_case_pack__lt=10).values('id', 'medicine_name', 'pack_size','total_case_pack','unit_price', 'stocks')
    context = {
        'low_stock_data':low_stock_data,
    }
    return render(request,'medicine_stock/low-stock.html',context)    


#--------Bottle Breakage
@login_required
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
                        return redirect('create_bottle_breakage')
                    else:
                        medicine_stock.total_case_pack -= bottle_breakage.lost_quantity
                        medicine_stock.save()
                except MedicineModel.DoesNotExist:
                    messages.warning(request, "Medicine data not found.")
                    return redirect('create_bottle_breakage')
            
            bottle_breakage.save()
            messages.success(request, "Bottle breakage recorded successfully.")
            return redirect('bottle_breakage_list')
    else:
        form = BottleBreakageForm()
    
    return render(request, "bottle_breakage/add-bottle-breakage.html", {"form": form})

# Update Bottle Breakage Entry
@login_required
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

# Delete Bottle Breakage Entry
@login_required
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
def bottle_breakage_list(request):
    bottle_breakages = BottleBreakageModel.objects.all()
    return render(request, "bottle_breakage/bottle-breakage-list.html", {"bottle_breakages": bottle_breakages})


#---------Order Functionalities
@login_required
def order_generate():
    return f"ORD-{random.randint(100000, 999999)}"

@login_required
def order_list(request):
    # Get the selected order status from GET parameter (default is 'All')
    order_status_filter = request.GET.get('status', 'All')
    
    if order_status_filter == 'All':
        orders = OrderModel.objects.annotate(
            total_items=Count('order_items'),  # Count the number of items in each order
            total_price=Sum('order_items__total_price'),  # Sum the total price of items in each order
            total_medicine_quantity=Sum('order_items__medicine_quantity')  # Sum the medicine quantities in each order
        )
    else:
        orders = OrderModel.objects.filter(order_status=order_status_filter).annotate(
            total_items=Count('order_items'),
            total_price=Sum('order_items__total_price'),
            total_medicine_quantity=Sum('order_items__medicine_quantity')
        )

    return render(request, 'orders/order-list.html', {'orders': orders, 'order_status_filter': order_status_filter})


@login_required
def order_create(request):
    medicines = MedicineModel.objects.all()  # Fetch all medicines
    
    if request.method == "POST":
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save(commit=False)

            # Generate unique order number
            while True:
                order_no = order_generate()
                if not OrderModel.objects.filter(order_no=order_no).exists():
                    break

            order.order_no = order_no
            order.created_by = request.user
            order.total_amount = Decimal(0)
            order.save()

            # Processing multiple order items
            medicines_ids = request.POST.getlist('medicine')
            quantities = request.POST.getlist('medicine_quantity')

            for i in range(len(medicines_ids)):
                try:
                    medicine = MedicineModel.objects.get(id=medicines_ids[i])
                    medicine_quantity = int(quantities[i])

                    if medicine_quantity > medicine.total_case_pack:
                        messages.error(request, f"Stock not available for {medicine.medicine_name}")
                        order.delete()
                        return redirect('order_create')

                    unit_price = Decimal(medicine.unit_price)
                    total_price = medicine_quantity * unit_price

                    OrderItemModel.objects.create(
                        order=order,
                        medicine=medicine,
                        medicine_quantity=medicine_quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    # Deduct stock
                    medicine.total_case_pack -= medicine_quantity
                    medicine.save()

                    order.total_amount += total_price

                except MedicineModel.DoesNotExist:
                    messages.error(request, "Invalid medicine selection.")
                    order.delete()
                    return redirect('order_create')

            order.total_amount += order.tax - order.discount
            order.save()

            messages.success(request, "Order created successfully!")
            return redirect('order_list')

    else:
        order_form = OrderForm()

    return render(request, 'orders/add-order.html', {'order_form': order_form, 'medicines': medicines})

@login_required
def order_update(request, pk):
    order = get_object_or_404(OrderModel, id=pk)  # Get the order to be updated
    medicines = MedicineModel.objects.all()  # Fetch all medicines
    
    if request.method == "POST":
        order_form = OrderForm(request.POST, instance=order)

        if order_form.is_valid():
            updated_order = order_form.save(commit=False)

            # Update order total amount
            updated_order.total_amount = Decimal(0)
            updated_order.save()

            # Processing multiple order items
            medicines_ids = request.POST.getlist('medicine')
            quantities = request.POST.getlist('medicine_quantity')

            # First, remove old order items (if any)
            order_items = order.order_items.all()  # Fixed here
            for item in order_items:
                item.medicine.total_case_pack += item.medicine_quantity  # Restoring the stock
                item.medicine.save()
                item.delete()

            # Adding new order items
            for i in range(len(medicines_ids)):
                try:
                    medicine = MedicineModel.objects.get(id=medicines_ids[i])
                    medicine_quantity = int(quantities[i])

                    if medicine_quantity > medicine.total_case_pack:
                        messages.error(request, f"Stock not available for {medicine.medicine_name}")
                        return redirect('order_update', order_id=order.id)

                    unit_price = Decimal(medicine.unit_price)
                    total_price = medicine_quantity * unit_price

                    OrderItemModel.objects.create(
                        order=updated_order,
                        medicine=medicine,
                        medicine_quantity=medicine_quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    # Deduct stock
                    medicine.total_case_pack -= medicine_quantity
                    medicine.save()

                    updated_order.total_amount += total_price

                except MedicineModel.DoesNotExist:
                    messages.error(request, "Invalid medicine selection.")
                    return redirect('order_update', order_id=order.id)

            updated_order.total_amount += updated_order.tax - updated_order.discount
            updated_order.save()

            messages.success(request, "Order updated successfully!")
            return redirect('order_list')

    else:
        order_form = OrderForm(instance=order)

    return render(request, 'orders/update-order.html', {
        'order_form': order_form, 
        'medicines': medicines, 
        'order': order,
        'order_items': order.order_items.all()  # Fixed here to access related order items
    })

@login_required
def order_delete(request, pk):
    order = get_object_or_404(OrderModel, pk=pk)

    for order_item in order.order_items.all():
        medicine = order_item.medicine
        medicine.total_case_pack += order_item.medicine_quantity
        medicine.save()

    order.delete()
    messages.success(request, "Order deleted successfully!")
    return redirect('order_list')

@login_required
def invoice_list(request):
    # Use aggregate to get the sum of medicine quantity and count of order items
    orders = OrderModel.objects.annotate(
        total_items=Count('order_items'),  # Count the number of items in each order
        total_price=Sum('order_items__total_price'),  # Sum the total price of items in each order
        total_medicine_quantity=Sum('order_items__medicine_quantity')  # Sum the medicine quantities in each order
    )
    
    return render(request, 'invoice-list.html', {'orders': orders})

@login_required
def invoice(request, order_id):
    # Fetch the order with the given order_id and related order items
    order = get_object_or_404(OrderModel, id=order_id)
    order_items = OrderItemModel.objects.filter(order=order)
    subtotal = sum(item.total_price for item in order_items)
    print("sub total: ",subtotal)

    # Pass the order and order items to the template
    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
    }
    return render(request, 'invoice.html', context)