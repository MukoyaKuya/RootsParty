
import os
import sys
import django
from django.core.management import call_command
from pathlib import Path

# Setup Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import os
from dotenv import load_dotenv

load_dotenv()

# Set env var for Django to pick up
if not os.environ.get('DATABASE_URL'):
     print("Warning: DATABASE_URL not found in environment, Django settings might fail if not configured elsewhere.")

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
