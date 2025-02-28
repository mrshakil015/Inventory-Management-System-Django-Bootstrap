from .models import NotificationModel, InventoryUser

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
            # Get the first user_access_list value or None if empty
            user_access = InventoryUser.objects.filter(username=request.user.username).values_list('user_access_list', flat=True).first()
 
            user_access_items = user_access.split(',') if user_access else []
            print("user access items: ",user_access_items)
            
            return {'user_access_items': user_access_items}
        except InventoryUser.DoesNotExist:
            return {'user_access_items': []}
    return {'user_access_items': []}
