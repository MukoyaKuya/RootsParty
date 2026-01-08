import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_aPjBTZvw8cD2@ep-autumn-math-ahlr3cf2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
django.setup()

from core.models import County

# Get all counties with their presence status
counties = County.objects.all().order_by('name')

print("Counties in database with presence status:")
print("=" * 60)
for county in counties:
    # Normalize name for matching (like JavaScript does)
    normalized = county.name.lower().replace(' ', '').replace('-', '').replace("'", "")
    print(f"{county.name:20s} | {county.presence_status:10s} | Key: {normalized}")

print("\n" + "=" * 60)
print(f"Total counties: {counties.count()}")

# Group by status
from collections import Counter
status_counts = Counter(c.presence_status for c in counties)
print("\nCounts by status:")
for status, count in status_counts.items():
    print(f"  {status}: {count}")
