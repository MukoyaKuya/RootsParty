from django.core.management.base import BaseCommand
from core.models import County

class Command(BaseCommand):
    help = 'Checks for specific problem counties using substring matching.'

    def handle(self, *args, **kwargs):
        problem_counties = ['Elgoyo', 'Homa', 'Murang', 'Nairobi', 'Tharaka', 'Trans']
        found_counties = []

        for term in problem_counties:
            matches = County.objects.filter(name__icontains=term)
            for c in matches:
                found_counties.append(c.name)

        self.stdout.write("Found Counties:")
        for name in sorted(list(set(found_counties))):
            self.stdout.write(f"- {name}")
