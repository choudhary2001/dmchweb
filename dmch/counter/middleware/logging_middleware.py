# myapp/middleware/logging_middleware.py
import json
from django.utils.deprecation import MiddlewareMixin
from counter.models import UserLog

class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user if request.user.is_authenticated else None
        database_name = request.session.get('database_name', 'default')  # Customize how you get the database name
        operation = request.path
        if request.method == 'POST':
            post_data = json.dumps(request.POST.dict())
        else:
            post_data = json.dumps(request.GET.dict())
        ip_address = request.META.get('REMOTE_ADDR')
        device_type = request.META.get('HTTP_USER_AGENT', 'unknown')
        print(user, database_name, operation)
        UserLog.objects.create(
            user=user,
            database_name=database_name,
            operation=operation,
            post_data=post_data,
            ip_address=ip_address,
            device_type=device_type
        )

    def process_response(self, request, response):
        # You can add additional logging for responses if needed
        return response
