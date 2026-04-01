# Shree1/middleware.py
from django.utils.deprecation import MiddlewareMixin

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Yeh teen lines browser ko back button par purana data dikhane se rokti hain
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
        return response