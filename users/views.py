# Standard library imports
import random
from datetime import datetime

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

# Local imports
from .forms import JoinForm
from .models import Member
from core.models import County

def get_client_ip(group, request):
    """
    Client IP address usually in X-Forwarded-For because of Cloud Run proxy.
    Format: 'client, proxy1, proxy2' -> We want 'client'
    
    Args:
        group: Rate limit group (required by django-ratelimit, not used here)
        request: Django request object
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from django.conf import settings
# ... (imports)

@ratelimit(key=get_client_ip, rate='5/m', block=True)
def join(request):
    if request.method == "POST":
        form = JoinForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    member = form.save()
                
                request.session['new_member_id'] = member.id
                return redirect('join_success')
            except Exception as e:
                # Should rarely happen given form validation check for uniqueness
                messages.error(request, f'An error occurred: {str(e)}')
        else:
             # Form errors will be in form.errors
             for field, errors in form.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}")
    else:
        form = JoinForm()

    counties = County.objects.all().order_by('name')
    return render(request, 'users/join.html', {
        'counties': counties, 
        'form': form,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    })

def join_coordinator(request):
    if request.method == "POST":
        # Personal Info
        surname = request.POST.get('surname')
        other_names = request.POST.get('other_names')
        full_name = f"{surname} {other_names}".strip()
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
            return render(request, 'users/join_coordinator.html', {'counties': counties})
            
        try:
            # Get County object if selected
            county_obj = None
            if county_id:
                try:
                    county_obj = County.objects.get(id=county_id)
                except County.DoesNotExist:
                    pass

            with transaction.atomic():
                member = Member.objects.create(
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
                    polling_center=polling_center,
                    is_coordinator_applicant=True  # Mark as coordinator applicant
                )
            # Store member ID in session for the success page
            request.session['new_member_id'] = member.id
            return redirect('join_success')
        except IntegrityError:
            messages.error(request, 'Comrade with this ID Number already registered!')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join_coordinator.html', {'counties': counties})
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            counties = County.objects.all().order_by('name')
            return render(request, 'users/join_coordinator.html', {'counties': counties})

    # GET request
    counties = County.objects.all().order_by('name')
    return render(request, 'users/join_coordinator.html', {
        'counties': counties,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    })

def check_id_number(request):
    id_number = request.GET.get('id_number')
    if id_number and Member.objects.filter(id_number=id_number).exists():
         return HttpResponse('<span class="text-roots-red font-bold uppercase block mt-1 bg-roots-black text-white p-2">⚠️ Error: Comrade already registered!</span>')
    return HttpResponse('')

@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def seed_members_view(request):
    try:
        from .tasks import seed_members_task
        task = seed_members_task.delay(target_count=75000)
        return HttpResponse(f"""
            <h1>Seeding Triggered!</h1>
            <p>Task ID: {task.id}</p>
            <p>The seeding is now running in the background via Celery.</p>
            <p>Check the admin panel or your Celery worker logs for progress.</p>
            <a href="/">Back to HQ</a>
        """)
    except Exception as e:
        return HttpResponse(f"Error triggering seeding: {str(e)}")

def join_success(request):
    member_id = request.session.get('new_member_id')
    member = None
    if member_id:
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            pass
    return render(request, 'users/success.html', {'member': member})


def download_card(request, uuid):
    """Generate membership card PDF (delegates to service layer)."""
    member = get_object_or_404(Member, uuid=uuid)
    try:
        from .services import build_member_card_pdf
        buffer = build_member_card_pdf(member)
    except ImportError:
        return HttpResponse(
            "QR code library not installed. Please install 'qrcode[pil]' and 'reportlab' to use this feature.",
            status=500,
        )
    except Exception as e:
        return HttpResponse(f"Error generating card: {str(e)}", status=500)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="roots_party_card_{member.id_number}.pdf"',
    })
