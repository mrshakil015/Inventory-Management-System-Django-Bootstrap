import os
import django

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_management.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "ethical"
email = "shakil@ethicalden.com"
password = "den"
first_name = "Ethical"
last_name = "Den"

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    user.first_name = first_name
    user.last_name = last_name
    user.role = 'Admin'
    user.save()
    print("Superuser with Admin role created successfully!")
else:
    print("Superuser already exists!")
