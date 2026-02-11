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
    # Globally cached site settings
    settings = cache.get('site_settings_singleton')
    if settings is None:
        settings = SiteSettings.get_settings()
        cache.set('site_settings_singleton', settings, 3600)

    active_splash = None
    # Only show splash screen on the homepage
    if request.path == '/':
        try:
            active_splash = Splash.get_active()
        except Exception:
            active_splash = None

    return {
        'site_settings': settings,
        'splash': active_splash
    }
