from django.shortcuts import render
from functools import wraps
from .models import InventoryUser
from django.core.cache import cache

def user_has_access(*required_permissions):  # Accept multiple permissions
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Try to get the cached access list for the user
                cache_key = f"user_access_{request.user.username}"
                user_access_items = cache.get(cache_key)
                
                # If the access list is not cached, fetch from the database and cache it
                cache.delete(cache_key)
                if user_access_items is None:
                    user_access_items = InventoryUser.objects.filter(username=request.user.username).values_list('user_access_list', flat=True).first()
                    user_access_items = user_access_items.split(',') if user_access_items else []
                    cache.set(cache_key, user_access_items, timeout=600)  # Cache for 10 minutes
                    cache.delete(cache_key)

                # Check if any of the required permissions exist in the user's access list
                if any(permission in user_access_items for permission in required_permissions):
                    return view_func(request, *args, **kwargs)
            # If no permission is found, deny access
            return render(request, 'auth/permission-denied.html', status=403)
        
        return _wrapped_view
    return decorator
