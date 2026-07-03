from django.utils.deprecation import MiddlewareMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

class NoCacheMiddleware(MiddlewareMixin):
    """
    Middleware to disable caching for specific URL patterns.
    This ensures that when a user logs out, going back to restricted pages won't work.
    """
    def process_response(self, request, response):
        if not hasattr(request, 'path_info'):
            return response
            
        path = request.path_info.lower()
        
        # Apply strict cache control to protected apps
        # Exclude static files and public areas if necessary
        if (
            path.startswith('/adminapp/') or 
            path.startswith('/vendorapp/') or 
            path.startswith('/customerapp/')
        ):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
        return response
