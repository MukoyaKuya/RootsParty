"""
Context processors for Roots Party platform.
Makes site settings available to all templates.
"""
from .models_site_settings import SiteSettings
from .models_splash import Splash


def site_settings(request):
    """
    Add site settings to template context.
    # Safe fetch for splash screen to avoid 500 errors if table doesn't exist yet
    try:
        active_splash = Splash.get_active()
    except Exception:
        active_splash = None

    return {
        'site_settings': SiteSettings.get_settings(),
        'splash': active_splash
    }
