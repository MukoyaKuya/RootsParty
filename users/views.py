# Standard library imports
import random
import logging
from datetime import datetime

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError, transaction
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

# Local imports
from .forms import JoinForm, CoordinatorRecaptchaForm, CoordinatorApplicationForm
from .models import Member
from core.models import County

logger = logging.getLogger(__name__)

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
            except Exception:
                # Should rarely happen given form validation check for uniqueness
                logger.exception("Member registration failed")
                messages.error(request, 'An error occurred while saving your registration. Please try again.')
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

@ratelimit(key=get_client_ip, rate='5/m', block=True)
def join_coordinator(request):
    if request.method == "POST":
        form = CoordinatorApplicationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    member = form.save()
                request.session['new_member_id'] = member.id
                return redirect('join_success')
            except IntegrityError:
                messages.error(request, 'Comrade with this ID Number already registered!')
            except Exception:
                logger.exception("Coordinator application failed")
                messages.error(request, 'An error occurred while saving your application. Please try again.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CoordinatorApplicationForm()

    counties = County.objects.all().order_by('name')
    return render(request, 'users/join_coordinator.html', {
        'counties': counties,
        'form': form,
        'recaptcha_form': form,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    })

@ratelimit(key=get_client_ip, rate='30/m', block=True)
def check_id_number(request):
    """
    Check if ID is already registered. Returns same empty response for all cases
    to avoid ID enumeration; duplicate check is performed on form submit.
    """
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
    except Exception:
        logger.exception("Member seeding failed to start")
        return HttpResponse("Error triggering seeding.", status=500)

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
    """Trigger async generation of membership card, or serve if ready."""
    member = get_object_or_404(Member, uuid=uuid)
    
    if member.membership_card:
        return FileResponse(member.membership_card, as_attachment=True)
        
    # Trigger the task
    from users.tasks import generate_member_card_task
    generate_member_card_task.delay(member.uuid)
    
    return render(request, 'users/card_processing.html', {'member': member})

def check_card_status(request, uuid):
    member = get_object_or_404(Member, uuid=uuid)
    if member.membership_card:
        return render(request, 'users/partials/card_ready.html', {'member': member})
    return render(request, 'users/partials/card_status.html', {'member': member})
