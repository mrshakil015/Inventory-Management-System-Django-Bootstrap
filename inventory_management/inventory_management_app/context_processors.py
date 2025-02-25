from .models import NotificationModel

def notifications(request):
    notifications = NotificationModel.objects.all().order_by('-created_at')
    return {
        'notifications': notifications,
    }
