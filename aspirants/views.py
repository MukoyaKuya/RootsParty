from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import Sum, Count, Q, Prefetch
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from .models import Aspirant, AspirantRegistration, LeadershipRole
from .forms import AspirantRegistrationForm
from .services import build_aspirant_profile_pdf, build_aspirants_report_pdf
from core.models import County, Constituency

@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def aspirant_registration(request, draft_token=None):
    """View for aspirant registration with rate limiting and draft support"""
    # Check if rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, "Too many submission attempts. Please try again later.")
        return render(request, 'aspirants/aspirant_registration.html', {
            'form': AspirantRegistrationForm(),
            'rate_limited': True
        })
    
    # Check if resuming a draft
    instance = None
    if draft_token:
        instance = AspirantRegistration.objects.filter(draft_token=draft_token, status='draft').first()
        if not instance:
            messages.error(request, "Draft application not found or already submitted.")
            return redirect('aspirant_registration')
    
    if request.method == 'POST':
        form = AspirantRegistrationForm(request.POST, request.FILES, instance=instance)
        
        # Check which button was clicked
        is_draft = 'save_draft' in request.POST
        
        if is_draft:
            # Save as draft - only validate basic fields
            if form.is_valid() or True:  # Allow partial save
                aspirant_reg = form.save(commit=False)
                aspirant_reg.status = 'draft'
                aspirant_reg.save()
                messages.success(request, "Draft saved! Use the link below to continue later.")
                return render(request, 'aspirants/aspirant_draft_saved.html', {'aspirant': aspirant_reg})
        else:
            if form.is_valid():
                aspirant_reg = form.save(commit=False)
                aspirant_reg.status = 'submitted'
                aspirant_reg.save()
                messages.success(request, "Registration successful!")
                return render(request, 'aspirants/aspirant_registration_success.html', {'aspirant': aspirant_reg})
    else:
        form = AspirantRegistrationForm(instance=instance)
    
    counties = County.objects.all().order_by('name')
    return render(request, 'aspirants/aspirant_registration.html', {
        'form': form,
        'is_draft_resume': instance is not None,
        'counties': counties
    })

def aspirant_status(request):
    """View for checking application status"""
    aspirant = None
    searched = False
    
    if request.method == 'POST':
        id_number = request.POST.get('id_number', '').strip()
        searched = True
        if id_number:
            aspirant = AspirantRegistration.objects.filter(
                id_number=id_number
            ).exclude(status='draft').first()
    
    return render(request, 'aspirants/aspirant_status.html', {
        'aspirant': aspirant,
        'searched': searched
    })

@require_http_methods(["GET"])
def check_aspirant_id(request):
    """Ajax check for duplicate ID number in aspirants"""
    id_number = request.GET.get('id_number')
    if id_number and AspirantRegistration.objects.filter(id_number=id_number).exists():
        return HttpResponse('<span class="text-roots-red font-bold uppercase block mt-1 bg-roots-black text-white p-2">⚠️ Error: Comrade already has an application!</span>')
    return HttpResponse('')

def aspirant_list(request):
    """List all aspirants with filtering"""
    role = request.GET.get('role', 'all')
    aspirants = Aspirant.objects.filter(is_active=True)
    
    if role != 'all':
        aspirants = aspirants.filter(role=role)
        
    return render(request, 'aspirants/aspirant_list.html', {
        'aspirants': aspirants,
        'current_role': role
    })

def aspirant_detail(request, aspirant_id):
    """Generic detail view for any aspirant"""
    aspirant = get_object_or_404(Aspirant, id=aspirant_id)
    return render(request, 'aspirants/aspirant_detail.html', {'aspirant': aspirant})

def mp_list(request):
    """List of counties for MP selection"""
    # Only show counties that have constituencies populated
    
    # Annotate with count of active MP aspirants
    counties = County.objects.annotate(
        c_count=Count('constituencies', distinct=True),
        aspirant_count=Count('aspirant_profiles', filter=Q(aspirant_profiles__is_active=True, aspirant_profiles__role='mp'), distinct=True)
    ).filter(c_count__gt=0).order_by('name')
    
    return render(request, 'aspirants/mp_list.html', {'counties': counties})

def mp_county_detail(request, slug):
    """List constituencies in a county"""
    county = get_object_or_404(County, slug=slug)
    
    # Prefetch active MP candidates
    active_mps = Aspirant.objects.filter(is_active=True, role='mp')
    constituencies = county.constituencies.prefetch_related(
        Prefetch('aspirant_profiles', queryset=active_mps, to_attr='active_mps')
    ).order_by('name')
    
    return render(request, 'aspirants/mp_county_detail.html', {
        'county': county,
        'constituencies': constituencies
    })

def mp_candidate_detail(request, constituency_slug):
    """Detail view for MP Candidate (Now Aspirant type MP)"""
    constituency = get_object_or_404(Constituency, slug=constituency_slug)
    # Get the active MP aspirant
    candidate = Aspirant.objects.filter(constituency=constituency, role='mp', is_active=True).first()
    
    return render(request, 'aspirants/mp_candidate_detail.html', {
        'constituency': constituency,
        'candidate': candidate
    })

@staff_member_required
def download_aspirant_pdf(request, aspirant_id):
    """Generate PDF profile for an aspirant (delegates to service layer)."""
    aspirant = get_object_or_404(AspirantRegistration, id=aspirant_id)
    buffer = build_aspirant_profile_pdf(aspirant)
    filename = f"Profile_{aspirant.surname}_{aspirant.id_number}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)

@staff_member_required
def download_aspirants_list_pdf(request):
    """Generate a full PDF report of all aspirants (delegates to service layer)."""
    buffer = build_aspirants_report_pdf()
    filename = f"Roots_Aspirants_Report_{timezone.now().strftime('%Y%m%d')}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)

def role_detail(request, slug):
    """Detail view for leadership roles"""
    role = get_object_or_404(LeadershipRole, slug=slug)
    return render(request, 'aspirants/role_detail.html', {'role': role})
