"""
Context processors for Roots Party platform.
Makes site settings available to all templates.
"""
from .models_site_settings import SiteSettings
from .models_splash import Splash


def site_settings(request):
    """
    Add site settings to template context.
    return {
        'site_settings': SiteSettings.get_settings(),
        'splash': Splash.get_active()
    }
