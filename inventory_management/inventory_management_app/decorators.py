from django.shortcuts import render
from functools import wraps
from .models import InventoryUser
from django.core.cache import cache

def user_has_access(required_permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                cache_key = f"user_access_{request.user.username}"
                user_access_items = cache.get(cache_key)
                
                if user_access_items is None:
                    user_access_items = InventoryUser.objects.filter(username=request.user.username).values_list('user_access_list', flat=True).first()
                    user_access_items = user_access_items.split(',') if user_access_items else []
                    cache.set(cache_key, user_access_items, timeout=600)  # Cache for 10 minutes
                
                if required_permission in user_access_items:
                    return view_func(request, *args, **kwargs)

            return render(request, 'auth/permission-denied.html', status=403)
        return _wrapped_view
    return decorator
