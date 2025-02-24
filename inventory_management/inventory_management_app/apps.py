# inventory_management_app/apps.py
from django.apps import AppConfig


class InventoryManagementAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_management_app'

    def ready(self):
        # Import the signals module to ensure they are loaded when the app is ready
        import inventory_management_app.signals  # Adjust the import based on your app structure
