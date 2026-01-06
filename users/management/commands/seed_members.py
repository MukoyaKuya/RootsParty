import random
from django.core.management.base import BaseCommand
from users.models import Member

class Command(BaseCommand):
    help = 'Seeds the database with 75,000 members'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding members...')
        
        first_names = [
            'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 
            'Kevin', 'Brian', 'Samuel', 'Peter', 'Daniel', 'Paul', 'Francis', 'Dennis', 'George',
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica',
            'Faith', 'Esther', 'Grace', 'Rose', 'Alice', 'Mercy', 'Caroline', 'Joyce', 'Ann',
            'Beatrice', 'Jane', 'Maureen', 'Irene', 'Sarah', 'Sharon', 'Michelle', 'Emily'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson',
            'Mwangi', 'Njoroge', 'Kamau', 'Otieno', 'Ochieng', 'Odhiambo', 'Kipkorir', 'Koech',
            'Chebet', 'Kimani', 'Maina', 'Wanjiku', 'Muthoni', 'Njeri', 'Mohamed', 'Ali', 'Juma',
            'Owino', 'Achieng', 'Wanjala', 'Wafula', 'Nyongesa', 'Mutua', 'Musyoka', 'Muli',
            'Nzioka', 'Abdalla', 'Hassan', 'Kariuki', 'Njenga', 'Garcia', 'Martinez', 'Robinson'
        ]
        
        total_records = 75000
        batch_size = 5000
        
        # Get existing IDs to ensure uniqueness if any exist
        existing_ids = set(Member.objects.values_list('id_number', flat=True))
        
        members_to_create = []
        count = 0
        
        self.stdout.write(f'Generating {total_records} members...')
        
        for i in range(total_records):
            # Generate unique ID
            while True:
                # Random ID between 10M and 40M (typical Kenyan ID range) or wider
                id_num = str(random.randint(10000000, 40000000))
                if id_num not in existing_ids:
                    existing_ids.add(id_num)
                    break
            
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            
            # Random phone number
            prefix = random.choice(['07', '01'])
            phone = f"{prefix}{random.randint(10000000, 99999999)}"
            
            members_to_create.append(Member(
                full_name=full_name,
                id_number=id_num,
                phone_number=phone
            ))
            
            if len(members_to_create) >= batch_size:
                Member.objects.bulk_create(members_to_create)
                count += len(members_to_create)
                self.stdout.write(f'Created {count} members...')
                members_to_create = []

        if members_to_create:
            Member.objects.bulk_create(members_to_create)
            count += len(members_to_create)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} members'))
