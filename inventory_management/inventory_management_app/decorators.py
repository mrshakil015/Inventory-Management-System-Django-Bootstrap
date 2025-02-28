# decorators.py

from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from .models import EmployeeModel

# decorators.py
def user_has_access(required_permission):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    # Fetch the user's access items from the EmployeeModel
                    user_access_items = EmployeeModel.objects.filter(employee_user=request.user).values_list('sidebar_access', flat=True)

                    # Split the string by commas and check if the required_permission is in the list
                    for access_items in user_access_items:
                        if required_permission in access_items.split(','):
                            return view_func(request, *args, **kwargs)
                except EmployeeModel.DoesNotExist:
                    pass
            # If the user does not have the permission, return a Forbidden response
            return render(request, 'auth/permission-denied.html', status=403)
        return _wrapped_view
    return decorator
