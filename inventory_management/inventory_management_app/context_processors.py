from .models import NotificationModel, EmployeeModel

def notifications(request):
    print("user is on the context processor notifications")
    notifications = NotificationModel.objects.all().order_by('-created_at')
    return {
        'notifications': notifications,
    }

def user_access_items(request):
    print("user is on the context processor")
    if request.user.is_authenticated:
        try:
            user = request.user
            user_access = EmployeeModel.objects.filter(employee_user=user).values_list('sidebar_access', flat=True).first()
    
            # Ensure user_access is not None and convert the comma-separated string into a list
            user_access_items = user_access.split(',') if user_access else []
            print("user access item: ", user_access_items)
            return {'user_access_items': user_access_items}
        except EmployeeModel.DoesNotExist:
            return {'user_access_items': []}
    return {'user_access_items': []}