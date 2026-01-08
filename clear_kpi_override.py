import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_aPjBTZvw8cD2@ep-autumn-math-ahlr3cf2-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
django.setup()

from core.models import PageContent

# Clear the KPI override for the about page
try:
    pc = PageContent.objects.get(page_name='about')
    pc.kpi_value = None
    pc.save()
    print(f"OK: Cleared KPI override for 'about' page. It will now use live database count.")
except PageContent.DoesNotExist:
    print("No PageContent found for 'about' - count will use database by default.")

# Show current member count
from users.models import Member
count = Member.objects.count()
print(f"Current member count in database: {count:,}")
