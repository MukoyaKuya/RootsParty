import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Vendor

# Set "Roots Official" as verified
vendor = Vendor.objects.filter(name="Roots Official").first()
if vendor:
    vendor.is_verified = True
    vendor.save()
    print(f"✓ Marked '{vendor.name}' as verified")
else:
    print("❌ Roots Official vendor not found")
