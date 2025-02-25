import datetime
from django.conf import settings
from django.shortcuts import redirect

class InactivityTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        last_activity = request.session.get('last_activity')

        if last_activity:
            last_activity_time = datetime.datetime.fromisoformat(last_activity)
            inactivity_duration = datetime.datetime.now() - last_activity_time
            timeout = datetime.timedelta(minutes=5)
            if inactivity_duration > timeout:
                from django.contrib.auth import logout
                logout(request)
                return redirect('user_login')
            
        request.session['last_activity'] = datetime.datetime.now().isoformat()

        response = self.get_response(request)
        return response
