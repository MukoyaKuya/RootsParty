"""
Context processors for Roots Party platform.
Makes site settings available to all templates.
"""
from .models_site_settings import SiteSettings


def site_settings(request):
    """
    Add site settings to template context.
    This makes the logo and other site settings available in all templates.
    """
    return {
        'site_settings': SiteSettings.get_settings()
    }
