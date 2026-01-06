
import random
import sys
from django.core.management.base import BaseCommand
from users.models import Member
from django.db import transaction

class Command(BaseCommand):
    help = 'Seeds the database with dummy members'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=75000, help='Number of members to create')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        self.stdout.write(f'Seeding {count} members...')

        first_names = ['John', 'Jane', 'James', 'Mary', 'Peter', 'Grace', 'David', 'Faith', 'Joseph', 'Esther', 'Samuel', 'Mercy', 'Daniel', 'Joyce', 'Francis', 'Alice', 'George', 'Ann', 'Michael', 'Rose', 'Wanjiku', 'Otieno', 'Nanjala', 'Kipchoge', 'Kamau', 'Muthoni', 'Ochieng', 'Achieng', 'Wanyama', 'Nafula', 'Kimani', 'Nyambura', 'Odhiambo', 'Anyango', 'Kipkorir', 'Chebet', 'Maina', 'Njeri', 'Omondi', 'Akoth', 'Mutua', 'Mwende', 'Rotich', 'Chepkemoi', 'Njoroge', 'Wairimu', 'Okoth', 'Atieno', 'Kibet', 'Jepkorir']
        last_names = ['Kamau', 'Omondi', 'Kiptoo', 'Wanjiku', 'Juma', 'Odhiambo', 'Mutua', 'Wafula', 'Maina', 'Otieno', 'Kariuki', 'Njeri', 'Mwangi', 'Anyango', 'Njoroge', 'Wairimu', 'Kipkorir', 'Achieng', 'Kimani', 'Nyambura', 'Kibet', 'Chebet', 'Rotich', 'Chepkemoi', 'Koech', 'Jepchirchir', 'Kosgei', 'Jepkemboi', 'Cheruiyot', 'Cherono', 'Rono', 'Jepleting', 'Tanui', 'Jepkosgei', 'Lelei', 'Chepkoech', 'Mutai', 'Chepngeno', 'Lagat', 'Chelagat', 'Choge', 'Jepchumba', 'Sang', 'Chepchirchir', 'Kiprotich', 'Chepkirui', 'Korir', 'Chebet', 'Kirui', 'Chepkorir']

        batch_size = 1000
        members = []
        
        # Determine starting ID to avoid conflicts
        last_member = Member.objects.order_by('-id').first()
        start_id_num = 10000000
        if last_member and last_member.id_number.isdigit():
             start_id_num = int(last_member.id_number) + 1
        elif last_member:
             start_id_num = 20000000 # Fallback

        print(f"Starting from ID: {start_id_num}")

        
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            id_number = str(start_id_num + i)
            phone = f"07{random.randint(10000000, 99999999)}"
            
            members.append(Member(full_name=full_name, id_number=id_number, phone_number=phone))
            
            if len(members) >= batch_size:
                with transaction.atomic():
                    Member.objects.bulk_create(members, ignore_conflicts=True)
                self.stdout.write(f'  Created batch of {batch_size} (Total: {i+1})')
                sys.stdout.flush()
                members = []

        if members:
            with transaction.atomic():
                Member.objects.bulk_create(members, ignore_conflicts=True)
            self.stdout.write(f'  Created final batch of {len(members)}')

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} members'))
