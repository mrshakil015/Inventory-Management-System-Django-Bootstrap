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

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    user.role = 'Admin'
    user.save()
    print("Superuser with Admin role created successfully!")
else:
    print("Superuser already exists!")
