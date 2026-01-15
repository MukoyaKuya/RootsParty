#!/usr/bin/env python
"""Run Django migrations"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("Running migrations...")
call_command('migrate')
print("\n✅ Migration completed!")
