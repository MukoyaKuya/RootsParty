"""
Populate carousel with default images
Run this AFTER the migration has been applied
"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, r'C:\Users\Little Human\Desktop\RootsParty')

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Setup Django
import django
django.setup()

from core.models import CarouselImage

print("=" * 60)
print("POPULATING CAROUSEL WITH DEFAULT IMAGES")
print("=" * 60)

# Create default carousel images
carousel_data = [
    {
        'title': 'Roots Party Movement',
        'image_path': 'carousel/carousel-1.jpg',
        'order': 1
    },
    {
        'title': 'Economic Liberation',
        'image_path': 'carousel/carousel-2.jpg',
        'order': 2
    },
    {
        'title': 'Youth Empowerment',
        'image_path': 'carousel/carousel-3.jpg',
        'order': 3
    },
]

created_count = 0
existing_count = 0

for data in carousel_data:
    carousel, created = CarouselImage.objects.get_or_create(
        title=data['title'],
        defaults={
            'image': data['image_path'],
            'order': data['order'],
            'is_active': True
        }
    )
    if created:
        print(f"✅ Created: {data['title']}")
        created_count += 1
    else:
        print(f"ℹ️  Already exists: {data['title']}")
        existing_count += 1

print("\n" + "=" * 60)
print(f"SUMMARY: Created {created_count}, Already existed {existing_count}")
print("=" * 60)
print("\n✅ Carousel population complete!")
print("Visit http://localhost:8080/ to see the carousel in action!")
print("Visit http://localhost:8080/admin/core/carouselimage/ to manage images")
print("=" * 60)
