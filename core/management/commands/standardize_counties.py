from django.core.management.base import BaseCommand
from core.models import County

class Command(BaseCommand):
    help = 'Standardize county names and remove empty duplicates'

    def handle(self, *args, **kwargs):
        # 1. DELETE Known Empty Duplicates (Losers)
        # Be careful not to delete if they have data now, but earlier check showed 0.
        deletions = [
            "Elgoyo Marakwet County",
            "Homabay County",
            "Nairobi County",
            "Trans Zoia County"
        ]
        
        for name in deletions:
            try:
                c = County.objects.get(name=name)
                if c.constituencies.count() == 0:
                    self.stdout.write(f"Deleting empty duplicate: {name}")
                    c.delete()
                else:
                    self.stdout.write(f"Skipping {name} - has data!")
            except County.DoesNotExist:
                pass

        # 2. RENAME Winners to Standard Format
        renames = {
            "Bomet": "Bomet County",
            "Elgeyo/Marakwet": "Elgeyo Marakwet County",
            "Homa Bay": "Homa Bay County",
            "Nairobi City": "Nairobi County",
            "Trans Nzoia": "Trans Nzoia County",
            "West Pokot": "West Pokot County",
            "Taita Taveta": "Taita Taveta County",
            "Tharaka Nithi": "Tharaka Nithi County",
            "Kericho": "Kericho County",
            "Kisii": "Kisii County" 
            # Add others if they lack "County" suffix and are the winners
        }

        for old, new in renames.items():
            try:
                c = County.objects.get(name=old)
                # Check if target name already exists (race condition or previous run)
                if County.objects.filter(name=new).exists():
                    self.stdout.write(f"Target '{new}' already exists. Merging...")
                    target = County.objects.get(name=new)
                    c.constituencies.update(county=target)
                    c.delete()
                else:
                    self.stdout.write(f"Renaming '{old}' to '{new}'")
                    c.name = new
                    from django.utils.text import slugify
                    c.slug = slugify(new)
                    c.save()
            except County.DoesNotExist:
                pass
                
        # 3. Final Sweep: Ensure all have "County" suffix
        for c in County.objects.all():
            if not c.name.lower().endswith(" county") and not c.name.lower().endswith(" city"):
                 msg = f"County '{c.name}' missing suffix."
                 new_name = f"{c.name} County"
                 if not County.objects.filter(name=new_name).exists():
                     c.name = new_name
                     c.slug = slugify(new_name)
                     c.save()
                     self.stdout.write(f"Standardized: {msg} -> {new_name}")

        self.stdout.write(self.style.SUCCESS("Standardization complete."))
