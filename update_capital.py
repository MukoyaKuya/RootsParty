import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import ManifestoItem, ManifestoEvidence
from django.utils.text import slugify

def update_capital_manifesto():
    # 1. Update/Get the Main Item
    # Using the slug from the original list: "Move Capital to Isiolo"
    target_slug = slugify("Move Capital to Isiolo")
    
    item, created = ManifestoItem.objects.get_or_create(
        slug=target_slug,
        defaults={'title': 'Move Capital to Isiolo'}
    )
    
    item.title = "Move Capital to Isiolo"
    item.icon = "🏗️"
    item.target_revenue = "Ease Congestion / Regional Growth"
    item.summary = "Decongest Nairobi. Build a futuristic, central capital in Isiolo."
    item.description = """
    Nairobi is choking. It was built for 500,000 people but now houses over 5 Million. The congestion, pollution, and lack of housing are suffocating our economy.
    
    It is time to start fresh. We will move the Administrative Capital to Isiolo.
    
    Isiolo is the geographic center of Kenya. It is the perfect strategic hub to connect the north, south, east, and west.
    
    By moving the seat of power, we will:
    1.  **Decongest Nairobi**: Let Nairobi remain the Commercial Hub (like New York) while Isiolo becomes the Administrative Hub (like Washington D.C.).
    2.  **Open up the North**: Northern Kenya has been neglected for 60 years. This move will bring infrastructure, water, and jobs to millions in the arid regions.
    3.  **Modern Planning**: We can build a Smart City from scratch, with proper zoning, modern sewage, and zero slums.
    """
    item.local_impact = """
    - Reduce Nairobi traffic jams, saving KES 100 Billion lost annually.
    - Transform Isiolo into a metropolis with an International Airport hub.
    - Create massive construction jobs for 10 years.
    - Equalize development across the nation, not just 'Kenya A'.
    """
    item.order = 8
    item.save()
    
    print(f"Updated Manifesto Item: {item.title}")

    # 2. Update Evidence (Clear existing first)
    item.evidence.all().delete()
    
    evidence_list = [
        {
            "country": "Egypt (New Cairo)",
            "description": "Egypt is currently building a new Administrative Capital to decongest Cairo. It features smart technology and will house 6.5 million people, proving that ancient cities can reinvent themselves."
        },
        {
            "country": "Tanzania (Dodoma)",
            "description": "Our neighbors successfully moved their capital from Dar es Salaam (Commercial) to Dodoma (Administrative) to centralize government services and spur inland development."
        },
        {
            "country": "Nigeria (Abuja)",
            "description": "Nigeria moved its capital from the overcrowded Lagos to the centrally located Abuja in 1991. Today, Abuja is one of Africa's best-planned and wealthiest cities."
        },
        {
            "country": "Brazil (Brasília)",
            "description": "Perhaps the most famous example. Brazil moved its capital inland to Brasília in 1960 to develop the interior of the country. It is now a UNESCO World Heritage site of modern planning."
        },
        {
            "country": "Indonesia (Nusantara)",
            "description": "Indonesia is actively moving its capital from the sinking Jakarta to Borneo (Nusantara) to save the old city and spread wealth."
        }
    ]
    
    for proof in evidence_list:
        ManifestoEvidence.objects.create(
            item=item,
            country=proof['country'],
            description=proof['description']
        )
        print(f"Added evidence for {proof['country']}")

if __name__ == '__main__':
    update_capital_manifesto()
