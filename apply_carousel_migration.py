"""
Direct database migration script for CarouselImage
This script will apply the migration directly to your PostgreSQL database
"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, r'C:\Users\Little Human\Desktop\RootsParty')

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Setup Django
import django
django.setup()

# Now run the migration
from django.core.management import execute_from_command_line

print("=" * 60)
print("RUNNING DJANGO MIGRATIONS")
print("=" * 60)

# Run migrate command
execute_from_command_line(['manage.py', 'migrate', 'core'])

print("\n" + "=" * 60)
print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nNext steps:")
print("1. Refresh your admin page")
print("2. Run: python populate_carousel_data.py")
print("=" * 60)
