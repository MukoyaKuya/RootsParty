from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Member
from django.db import IntegrityError, transaction
import random
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test

from core.models import County

def join(request):
    if request.method == "POST":
        # Personal Info
        surname = request.POST.get('surname')
        other_names = request.POST.get('other_names')
        full_name = f"{surname} {other_names}".strip() # Fallback for backward compatibility
        id_number = request.POST.get('id_number')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')
        
        # Demographics
        occupation = request.POST.get('occupation')
        ethnicity = request.POST.get('ethnicity')
        sex = request.POST.get('sex')
        special_interest = request.POST.get('special_interest')
        
        # Location
        county_id = request.POST.get('county')
        constituency = request.POST.get('constituency')
        ward = request.POST.get('ward')
        polling_center = request.POST.get('polling_center')

        # Basic validation
        if not id_number or not phone or not surname:
            messages.error(request, 'Please fill all required fields')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join.html', {'counties': counties})
            
        try:
            # Get County object if selected
            county_obj = None
            if county_id:
                try:
                    county_obj = County.objects.get(id=county_id)
                except County.DoesNotExist:
                    pass

            Member.objects.create(
                full_name=full_name,
                surname=surname,
                other_names=other_names,
                id_number=id_number,
                phone_number=phone,
                email=email,
                date_of_birth=date_of_birth if date_of_birth else None,
                occupation=occupation,
                ethnicity=ethnicity,
                sex=sex,
                special_interest=special_interest,
                county=county_obj,
                constituency=constituency,
                ward=ward,
                polling_center=polling_center
            )
            return render(request, 'users/success.html')
        except IntegrityError:
            messages.error(request, 'Comrade with this ID Number already registered!')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join.html', {'counties': counties})
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join.html', {'counties': counties})

    # GET request
    counties = County.objects.all().order_by('name')
    return render(request, 'users/join.html', {'counties': counties})

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
