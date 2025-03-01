import os
import django

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_management.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "dobson"
email = "drijendranrai3@gmail.com"
password = "homeo3"
first_name = "Dobson Homoeo"
last_name = "Pharmacy"

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    user.first_name = first_name
    user.last_name = last_name
    user.role = 'Admin'
    user_access_list = ['employee_management', 'employee_view', 'customer_management', 'customer_view', 'product_management', 'product_view', 'low_stocks', 'billing_management', 'inventory_report', 'wastage_report', 'billing_report']
    user.user_access_list = ','.join(user_access_list)
    user.save()
    print("Superuser with Admin role created successfully!")
else:
    print("Superuser already exists!")
