from django.shortcuts import render
from functools import wraps
from .models import EmployeeModel

def user_has_access(required_permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Fetch the user's access list from InventoryUser
                user_access_items = EmployeeModel.objects.filter(employee_user=request.user).values_list('user_access_list', flat=True)

                # Ensure we check non-empty user_access_list values
                for access_items in user_access_items:
                    if access_items:  # Ensure it's not None
                        if required_permission in access_items.split(','):
                            return view_func(request, *args, **kwargs)

            # If the user does not have the permission, return a Forbidden response
            return render(request, 'auth/permission-denied.html', status=403)
        return _wrapped_view
    return decorator
