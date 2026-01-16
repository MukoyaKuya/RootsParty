from django.core.management.base import BaseCommand
from core.models import County, Constituency
from django.db.models import Q

class Command(BaseCommand):
    help = 'Merges duplicate counties (e.g. "Vihiga" into "Vihiga County")'

    def handle(self, *args, **kwargs):
        # We assume the "County" suffixed ones are the "Original/Better" ones if they exist.
        # Or we just standardize on one.
        
        # Get all counties
        all_counties = County.objects.all()
        
        for county in all_counties:
            name = county.name
            
            # Check if this is a "Short Name" (e.g. Vihiga) and a "Long Name" (Vihiga County) exists
            if not name.lower().endswith(" county"):
                long_name = f"{name} County"
                matches = County.objects.filter(name__iexact=long_name)
                
                if matches.exists():
                    target_county = matches.first()
                    self.stdout.write(f"Found duplicate: '{name}' -> '{target_county.name}'")
                    
                    # Move constituencies
                    constituencies = county.constituencies.all()
                    count = constituencies.count()
                    if count > 0:
                        self.stdout.write(f" - Moving {count} constituencies...")
                        constituencies.update(county=target_county)
                        
                    # Delete the short name county
                    if county.members_count == 0 and county.offices_count == 0:
                         self.stdout.write(f" - Deleting '{name}'")
                         county.delete()
                    else:
                         self.stdout.write(f" - WARNING: '{name}' has members/offices, not deleting automatically.")
                         # If it has data, maybe we should merge the other way?
                         # For now, let's assume the API created clean new ones with 0 members.
            
            # Also check for " County" duplicates if API created "Vihiga County" and we had "Vihiga".
            # The API seemed to create "Vihiga" (short).
            
        self.stdout.write(self.style.SUCCESS("Cleanup complete."))
