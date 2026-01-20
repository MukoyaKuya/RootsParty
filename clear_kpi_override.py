import os
import django

from dotenv import load_dotenv

load_dotenv()

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if not os.environ.get("DATABASE_URL"):
    raise ValueError("DATABASE_URL must be set in .env")
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
