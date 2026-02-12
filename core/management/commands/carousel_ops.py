from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import CarouselImage

class Command(BaseCommand):
    help = 'Operations for the Carousel feature: migrations and seeding.'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')
        
        # Subcommand: migrate
        subparsers.add_parser('migrate', help='Run migrations for the carousel feature')
        
        # Subcommand: seed
        subparsers.add_parser('seed', help='Populate the carousel with default images')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'migrate':
            self.carousel_migrate()
        elif action == 'seed':
            self.carousel_seed()
        else:
            self.print_help('manage.py', 'carousel_ops')

    def carousel_migrate(self):
        self.stdout.write("Creating and applying migrations for the core app...")
        try:
            call_command('makemigrations', 'core')
            call_command('migrate', 'core')
            self.stdout.write(self.style.SUCCESS("✅ Carousel migrations applied successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Migration failed: {e}"))

    def carousel_seed(self):
        self.stdout.write("Populating carousel with default images...")
        carousel_data = [
            {'title': 'Roots Party Movement', 'image_path': 'carousel/carousel-1.jpg', 'order': 1},
            {'title': 'Economic Liberation', 'image_path': 'carousel/carousel-2.jpg', 'order': 2},
            {'title': 'Youth Empowerment', 'image_path': 'carousel/carousel-3.jpg', 'order': 3},
        ]
        
        created_count = 0
        existing_count = 0
        for data in carousel_data:
            _, created = CarouselImage.objects.get_or_create(
                title=data['title'],
                defaults={
                    'image': data['image_path'],
                    'order': data['order'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f"  ✅ Created: {data['title']}")
                created_count += 1
            else:
                self.stdout.write(f"  ℹ️  Already exists: {data['title']}")
                existing_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nSummary: Created {created_count}, Already existed {existing_count}"))
