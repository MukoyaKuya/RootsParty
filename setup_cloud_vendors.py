#!/usr/bin/env python
"""
Run migrations on Cloud database and set up default vendor
"""
import os
import django

# Use the production DATABASE_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import os
from dotenv import load_dotenv

load_dotenv()

# Set env var for Django to pick up
if not os.environ.get('DATABASE_URL'):
    raise ValueError("DATABASE_URL must be set in .env")

django.setup()

from django.core.management import call_command
from commerce.models import Vendor, Product

print("Running migrations on production database...")
call_command('migrate', '--noinput')

print("\nSetting up default vendor...")
vendor, created = Vendor.objects.get_or_create(
    name="Roots Official",
    defaults={
        'description': "The official merchandise store for the Roots Party of Kenya. Get your authentic t-shirts, caps, and flags here.",
        'contact_email': "shop@rootsparty.co.ke",
        'is_active': True,
        'is_verified': True
    }
)

if created:
    print(f"Created vendor: {vendor.name}")
else:
    print(f"Vendor already exists: {vendor.name}")
    vendor.is_verified = True
    vendor.save()
    print("Marked as verified")

# Assign orphan products to default vendor
orphans = Product.objects.filter(vendor__isnull=True)
count = orphans.count()
if count > 0:
    orphans.update(vendor=vendor)
    print(f"Migrated {count} orphan products to {vendor.name}")
else:
    print("No orphan products found")

print("\n✓ Production database setup complete!")
