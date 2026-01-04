import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ManifestoItem, ManifestoEvidence

updates = [
    {
        'slug': 'suspend-constitution',
        'evidence': [
             {'country': 'United Kingdom', 'desc': 'Operates without a single written constitution, allowing for flexibility and rapid adaptation to crises.'},
             {'country': 'Israel', 'desc': 'Uses Basic Laws instead of a rigid constitution, allowing the Knesset to govern effectively.'}
        ]
    },
    {
        'slug': 'move-capital',
        'evidence': [
            {'country': 'Brazil', 'desc': 'Moved capital from Rio de Janeiro to Brasília in 1960 to develop the interior of the country.'},
            {'country': 'Nigeria', 'desc': 'Moved from Lagos to Abuja to decongest the coastal city and promote unity.'},
            {'country': 'Tanzania', 'desc': 'Shifted administrative functions to Dodoma to centralize governance.'}
        ]
    },
    {
        'slug': 'federal-system',
        'evidence': [
            {'country': 'United States', 'desc': '50 states with autonomy allow for local laws that reflect local cultures and economies (e.g., California vs. Texas).'},
            {'country': 'Germany', 'desc': 'Strong federal states (Länder) drive regional economic powerhouses.'}
        ]
    },
    {
        'slug': 'deportations',
        'evidence': [
            {'country': 'Switzerland', 'desc': 'Strict work permit laws ensure Swiss citizens have priority for all jobs.'},
            {'country': 'Saudi Arabia', 'desc': 'Saudization policy requires companies to hire locals for specific sectors.'}
        ]
    },
    {
        'slug': 'shut-sgr',
        'evidence': [
            {'country': 'Malaysia', 'desc': 'Cancelled Chinese-funded pipeline and rail projects worth $22 billion to avoid debt traps.'},
            {'country': 'Sri Lanka', 'desc': 'A warning tale: Forced to lease Hambantota Port to China for 99 years after failing to service debt.'}
        ]
    }
]

for update in updates:
    try:
        item = ManifestoItem.objects.get(slug=update['slug'])
        print(f"Updating {item.title}...")
        
        # Add new evidence
        for ev in update['evidence']:
            ManifestoEvidence.objects.get_or_create(
                item=item, 
                country=ev['country'], 
                defaults={'description': ev['desc']}
            )
            
    except ManifestoItem.DoesNotExist:
        print(f"Item not found: {update['slug']}")

print("Manifesto content enriched successfully!")
