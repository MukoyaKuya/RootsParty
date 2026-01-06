from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Member
from django.db import transaction
import random
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test

def join(request):
    if request.method == "POST":
        # Create member
        # Basic validation
        if not request.POST.get('id_number') or not request.POST.get('phone'):
            return HttpResponse('<div class="text-roots-red font-bold">Please fill all fields</div>')
            
        Member.objects.create(
            full_name=request.POST.get('full_name'),
            id_number=request.POST.get('id_number'),
            phone_number=request.POST.get('phone')
        )
        
        # If HTMX, return just the success message content (we will create a partial or just toggle blocks)
        # But since we have success.html extending base, we need to be careful.
        # A simple fix if we don't have separate partials is to let it redirect or render.
        # For HTMX to work smoothly with full page templates, we usually use hx-target="body" or use a partial.
        # Let's assume we want to render the full success page for now, but cleaner.
        return render(request, 'users/success.html')
    return render(request, 'users/join.html')

def check_id_number(request):
    id_number = request.GET.get('id_number')
    if id_number and Member.objects.filter(id_number=id_number).exists():
         return HttpResponse('<span class="text-roots-red font-bold uppercase block mt-1 bg-roots-black text-white p-2">⚠️ Error: Comrade already registered!</span>')
    return HttpResponse('')

@user_passes_test(lambda u: u.is_superuser)
def seed_members_view(request):
    try:
        target_count = 75000
        current_count = Member.objects.count()
        
        if current_count >= target_count:
            # Reset KPI on finish
            from core.models import PageContent
            try:
                pc = PageContent.objects.get(page_name='about')
                pc.kpi_value = None
                pc.save()
            except:
                pass
            return HttpResponse(f"""
                <h1 style='color:green'>DONE! Total Members: {current_count}</h1>
                <p>You can close this page.</p>
            """)

        # Insert batch of 1000
        batch_limit = 1000
        members = []
        
        # Calculate distinct start id for this batch based on current count
        # This is a heuristic; assumes sequential execution
        start_id = 70000000 + current_count 
        
        first_names = ['John', 'Jane', 'James', 'Mary', 'Peter', 'Grace', 'David', 'Faith', 'Joseph', 'Esther', 'Samuel', 'Mercy', 'Daniel', 'Joyce', 'Francis', 'Alice', 'George', 'Ann', 'Michael', 'Rose', 'Wanjiku', 'Otieno', 'Nanjala', 'Kipchoge', 'Kamau', 'Muthoni', 'Ochieng', 'Achieng', 'Wanyama', 'Nafula', 'Kimani', 'Nyambura', 'Odhiambo', 'Anyango', 'Kipkorir', 'Chebet', 'Maina', 'Njeri', 'Omondi', 'Akoth', 'Mutua', 'Mwende', 'Rotich', 'Chepkemoi', 'Njoroge', 'Wairimu', 'Okoth', 'Atieno', 'Kibet', 'Jepkorir']
        last_names = ['Kamau', 'Omondi', 'Kiptoo', 'Wanjiku', 'Juma', 'Odhiambo', 'Mutua', 'Wafula', 'Maina', 'Otieno', 'Kariuki', 'Njeri', 'Mwangi', 'Anyango', 'Njoroge', 'Wairimu', 'Kipkorir', 'Achieng', 'Kimani', 'Nyambura', 'Kibet', 'Chebet', 'Rotich', 'Chepkemoi', 'Koech', 'Jepchirchir', 'Kosgei', 'Jepkemboi', 'Cheruiyot', 'Cherono', 'Rono', 'Jepleting', 'Tanui', 'Jepkosgei', 'Lelei', 'Chepkoech', 'Mutai', 'Chepngeno', 'Lagat', 'Chelagat', 'Choge', 'Jepchumba', 'Sang', 'Chepchirchir', 'Kiprotich', 'Chepkirui', 'Korir', 'Chebet', 'Kirui', 'Chepkorir']

        for i in range(batch_limit):
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            id_number = str(start_id + i)
            phone = f"07{random.randint(10000000, 99999999)}"
            
            members.append(Member(full_name=full_name, id_number=id_number, phone_number=phone))
            
        Member.objects.bulk_create(members, ignore_conflicts=True)
        
        new_total = Member.objects.count()
        remaining = target_count - new_total
        
        return HttpResponse(f"""
            <h1>Seeding Progress...</h1>
            <p>Added 1,000 members.</p>
            <p><strong>Total: {new_total} / {target_count}</strong></p>
            <p>Remaining: {remaining}</p>
            <p><em>Auto-refreshing in 1 second to continue...</em></p>
            <script>
                setTimeout(function(){{ window.location.reload(); }}, 1000);
            </script>
        """)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
