"""
Check current logo status in SiteSettings
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models_site_settings import SiteSettings

s = SiteSettings.get_settings()

print("=" * 60)
print("CURRENT LOGO STATUS")
print("=" * 60)
print(f"Has logo uploaded: {bool(s.logo)}")
if s.logo:
    print(f"Logo file name: {s.logo.name}")
    print(f"Logo URL: {s.logo.url}")
    print(f"Logo path: {s.logo.path if hasattr(s.logo, 'path') else 'N/A'}")
else:
    print("No logo uploaded - using default static logo")
    print("Default logo: /static/images/logo.png")
print("=" * 60)
print("\nTo upload a logo:")
print("1. Go to: http://localhost:8080/admin/core/sitesettings/1/change/")
print("2. Click 'Choose File' next to 'Logo'")
print("3. Select your clean logo image (without JuaGig watermark)")
print("4. Use the cropping tool if needed")
print("5. Click 'Save'")
print("6. Refresh your homepage (Ctrl+F5 to clear cache)")
