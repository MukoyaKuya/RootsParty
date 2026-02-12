from celery import shared_task
from django.core.files.base import ContentFile
import random
from users.models import Member

@shared_task
def seed_members_task(target_count=75000):
    """Background task to seed members up to target_count."""
    current_count = Member.objects.count()
    if current_count >= target_count:
        return f"Already at target: {current_count}"
    
    batch_limit = 1000
    first_names = ['John', 'Jane', 'James', 'Mary', 'Peter', 'Grace', 'David', 'Faith', 'Joseph', 'Esther', 'Samuel', 'Mercy', 'Daniel', 'Joyce', 'Francis', 'Alice', 'George', 'Ann', 'Michael', 'Rose', 'Wanjiku', 'Otieno', 'Nanjala', 'Kipchoge', 'Kamau', 'Muthoni', 'Ochieng', 'Achieng', 'Wanyama', 'Nafula', 'Kimani', 'Nyambura', 'Odhiambo', 'Anyango', 'Kipkorir', 'Chebet', 'Maina', 'Njeri', 'Omondi', 'Akoth', 'Mutua', 'Mwende', 'Rotich', 'Chepkemoi', 'Njoroge', 'Wairimu', 'Okoth', 'Atieno', 'Kibet', 'Jepkorir']
    last_names = ['Kamau', 'Omondi', 'Kiptoo', 'Wanjiku', 'Juma', 'Odhiambo', 'Mutua', 'Wafula', 'Maina', 'Otieno', 'Kariuki', 'Njeri', 'Mwangi', 'Anyango', 'Njoroge', 'Wairimu', 'Kipkorir', 'Achieng', 'Kimani', 'Nyambura', 'Kibet', 'Chebet', 'Rotich', 'Chepkemoi', 'Koech', 'Jepchirchir', 'Kosgei', 'Jepkemboi', 'Cheruiyot', 'Cherono', 'Rono', 'Jepleting', 'Tanui', 'Jepkosgei', 'Lelei', 'Chepkoech', 'Mutai', 'Chepngeno', 'Lagat', 'Chelagat', 'Choge', 'Jepchumba', 'Sang', 'Chepchirchir', 'Kiprotich', 'Chepkirui', 'Korir', 'Chebet', 'Kirui', 'Chepkorir']

    total_added = 0
    while current_count < target_count:
        members = []
        # Calculate distinct start id for this batch
        start_id = 70000000 + current_count + random.randint(1, 1000)
        
        for i in range(min(batch_limit, target_count - current_count)):
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            id_number = str(start_id + i)
            phone = f"07{random.randint(10000000, 99999999)}"
            
            members.append(Member(full_name=full_name, id_number=id_number, phone_number=phone))
            
        Member.objects.bulk_create(members, ignore_conflicts=True)
        current_count = Member.objects.count()
        total_added += len(members)
        
    return f"Seeding complete. Added approx {total_added} members. Total: {current_count}"

@shared_task
def generate_member_card_task(member_uuid):
    """Background task to generate and save a member card."""
    try:
        member = Member.objects.get(uuid=member_uuid)
        from .services import build_member_card_pdf
        buffer = build_member_card_pdf(member)
        
        filename = f"roots_party_card_{member.id_number}.pdf"
        member.membership_card.save(filename, ContentFile(buffer.read()), save=True)
        
        return f"Card generated and saved for {member.full_name}"
    except Exception as e:
        return f"Error generating member card: {str(e)}"
