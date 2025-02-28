from .models import NotificationModel, InventoryUser

def notifications(request):
    print("user is on the context processor notifications")
    notifications = NotificationModel.objects.all().order_by('-created_at')
    return {
        'notifications': notifications,
    }

def user_access_items(request):
    if request.user.is_authenticated:
        if 'user_access_items' not in request.session:
            user_access = InventoryUser.objects.filter(username=request.user.username).values_list('user_access_list', flat=True).first()
            user_access_items = user_access.split(',') if user_access else []
            request.session['user_access_items'] = user_access_items  # Cache in session
        return {'user_access_items': request.session['user_access_items']}
    return {'user_access_items': []}

