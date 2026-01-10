import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Vendor, Product

def migrate_vendors():
    # 1. Create Default Vendor
    vendor, created = Vendor.objects.get_or_create(
        name="Roots Official",
        defaults={
            'description': "The official merchandise store for the Roots Party of Kenya. Get your authentic t-shirts, caps, and flags here.",
            'contact_email': "shop@rootsparty.co.ke",
            'is_active': True
        }
    )
    
    if created:
        print(f"Created default vendor: {vendor.name}")
    else:
        print(f"Vendor already exists: {vendor.name}")

    # 2. Assign to Orphan Products
    orphans = Product.objects.filter(vendor__isnull=True)
    count = orphans.count()
    
    if count > 0:
        orphans.update(vendor=vendor)
        print(f"Migrated {count} products to {vendor.name}")
    else:
        print("No orphan products found.")

if __name__ == "__main__":
    migrate_vendors()
