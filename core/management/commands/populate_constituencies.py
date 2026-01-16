import json
import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import County, Constituency

class Command(BaseCommand):
    help = 'Populates constituencies from the Kenya Area Data API'

    def handle(self, *args, **kwargs):
        api_url = "https://kenyaareadata.vercel.app/api/areas?apiKey=keyPub1569gsvndc123kg9sjhg"
        
        self.stdout.write("Fetching data from API...")
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to fetch data: {e}"))
            return

        self.stdout.write(f"Successfully fetched data. Processing {len(data)} counties...")

        counties_updated = 0
        constituencies_created = 0

        for county_name, constituencies_data in data.items():
            # 1. Find or Create County
            # The API uses Title Case usually, but let's be flexible
            county_slug = slugify(county_name)
            
            # Try to find by slug first to avoid duplicates if name varies slightly
            county, created = County.objects.get_or_create(
                slug=county_slug,
                defaults={'name': county_name, 'presence_status': 'growing'}
            )
            
            if created:
                self.stdout.write(f"Created new county: {county_name}")
            
            counties_updated += 1
            
            # 2. Process Constituencies
            # constituencies_data is a dictionary where keys are Constituency names
            # and values are lists of Wards. We only need the keys.
            if isinstance(constituencies_data, dict):
                for const_name in constituencies_data.keys():
                    const_slug = slugify(const_name)
                    
                    # Ensure uniqueness within county context if needed, but simple get_or_create is safer
                    constituency, c_created = Constituency.objects.get_or_create(
                        county=county,
                        slug=const_slug,
                        defaults={'name': const_name}
                    )
                    
                    if c_created:
                        constituencies_created += 1
            
        self.stdout.write(self.style.SUCCESS(f"Done! Processed {counties_updated} counties. Created {constituencies_created} new constituencies."))
