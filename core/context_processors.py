"""
Context processors for Roots Party platform.
Makes site settings available to all templates.
"""
from django.core.cache import cache
from .models_site_settings import SiteSettings
from .models_splash import Splash


def site_settings(request):
    """
    Add site settings to template context.
    Uses caching to improve startup performance.
    """
    cache_key = 'site_global_context'
    context = cache.get(cache_key)

    if context is None:
        # Safe fetch for splash screen to avoid 500 errors if table doesn't exist yet or other DB issues
        try:
            active_splash = Splash.get_active()
        except Exception:
            active_splash = None

        context = {
            'site_settings': SiteSettings.get_settings(),
            'splash': active_splash
        }
        # Cache for 1 hour. Cache will be cleared on model save.
        cache.set(cache_key, context, 3600)

    return context
