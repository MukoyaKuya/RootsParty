"""
Management command to populate carousel images with default images
Run with: python manage.py populate_carousel
"""
from django.core.management.base import BaseCommand
from core.models import CarouselImage
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate carousel with default images'

    def handle(self, *args, **options):
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
                self.stdout.write(self.style.SUCCESS(f'Created carousel image: {data["title"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Carousel image already exists: {data["title"]}'))

        self.stdout.write(self.style.SUCCESS('Carousel population complete!'))
