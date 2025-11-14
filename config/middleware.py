class HealthCheckMiddleware:
    """
    Middleware for health check endpoint
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health/':
            from django.http import JsonResponse
            return JsonResponse({'status': 'healthy'})
        
        response = self.get_response(request)
        return response
