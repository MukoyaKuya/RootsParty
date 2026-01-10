import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import County

problem_counties = ['Elgoyo', 'Homa', 'Murang', 'Nairobi', 'Tharaka', 'Trans']
found_counties = []

for term in problem_counties:
    matches = County.objects.filter(name__icontains=term)
    for c in matches:
        found_counties.append(c.name)

print("Found Counties:")
for name in sorted(list(set(found_counties))):
    print(f"- {name}")
