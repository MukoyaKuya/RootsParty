
import os
import sys
import django
from django.core.management import call_command
from pathlib import Path

# Setup Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = "postgresql://neondb_owner:npg_aPjBTZvw8cD2@ep-autumn-math-ahlr3cf2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

django.setup()

output_file = 'cloud_backup.json'

print("Starting dumpdata...")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata', 
            exclude=['auth.permission', 'contenttypes', 'admin.logentry', 'sessions.session'],
            indent=2, 
            stdout=f
        )
    print(f"Successfully dumped data to {output_file}")
except Exception as e:
    print(f"Error dumping data: {e}")
