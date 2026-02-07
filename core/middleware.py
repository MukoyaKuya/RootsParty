"""
Cache monitoring middleware for tracking performance metrics.
"""

import time
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin


class CacheStatsMiddleware(MiddlewareMixin):
    """
    Middleware to add cache statistics and processing time headers.
    """
    
    def process_request(self, request):
        """Record request start time."""
        request._cache_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Add performance headers to response."""
        if hasattr(request, '_cache_start_time'):
            duration = time.time() - request._cache_start_time
            response['X-Processing-Time'] = f'{duration:.3f}s'
        
        # Add cache stats for admin users
        if request.user.is_authenticated and request.user.is_staff:
            from core.cache_utils import get_cache_stats
            stats =get_cache_stats()
            if stats:
                response['X-Cache-Hit-Rate'] = stats.get('hit_rate', 'N/A')
        
        return response
