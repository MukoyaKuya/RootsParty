#!/usr/bin/env python
"""
Script to create and run migrations for CarouselImage model
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now run the migration commands
from django.core.management import call_command

print("Creating migrations for core app...")
call_command('makemigrations', 'core')

print("\nRunning migrations...")
call_command('migrate')

print("\n✅ Migrations completed successfully!")
print("\nNext step: Run 'python manage.py populate_carousel' to add default images")
