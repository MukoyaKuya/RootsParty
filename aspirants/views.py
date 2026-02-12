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
            # Save as draft - allow partial save by bypassing strict form validation
            aspirant_reg = instance or AspirantRegistration()
            
            # Manually update fields from POST data
            for field_name in form.fields:
                if field_name in request.POST:
                    value = request.POST.get(field_name)
                    # For ForeignKeys, we need the actual object
                    if field_name == 'county' and value:
                        try:
                            value = County.objects.get(id=value)
                        except (County.DoesNotExist, ValueError):
                            value = None
                    setattr(aspirant_reg, field_name, value)
            
            # Handle files
            for file_name in request.FILES:
                setattr(aspirant_reg, file_name, request.FILES[file_name])
            
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

from django.db.models import Case, When, Value, IntegerField

def aspirant_list(request):
    """List all aspirants with filtering"""
    role = request.GET.get('role', 'all')
    aspirants = Aspirant.objects.filter(is_active=True)
    
    if role != 'all':
        aspirants = aspirants.filter(role=role)
    else:
        # Define priority for roles
        role_priority = Case(
            When(role='president', then=Value(1)),
            When(role='governor', then=Value(2)),
            When(role='senator', then=Value(3)),
            When(role='woman_rep', then=Value(4)),
            When(role='mp', then=Value(5)),
            When(role='mca', then=Value(6)),
            default=Value(7),
            output_field=IntegerField(),
        )
        aspirants = aspirants.order_by(role_priority, 'name')
        
    return render(request, 'aspirants/aspirant_list.html', {
        'aspirants': aspirants,
        'current_role': role
    })

def aspirant_detail(request, uuid):
    """Generic detail view for any aspirant"""
    aspirant = get_object_or_404(Aspirant, uuid=uuid)
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
def download_aspirant_pdf(request, uuid):
    """Trigger async generation of aspirant profile PDF, or serve if ready."""
    aspirant = get_object_or_404(AspirantRegistration, uuid=uuid)
    
    if aspirant.profile_pdf:
        return FileResponse(aspirant.profile_pdf, as_attachment=True)
        
    from aspirants.tasks import generate_aspirant_profile_pdf_task
    generate_aspirant_profile_pdf_task.delay(aspirant.uuid)
    
    return render(request, 'aspirants/profile_processing.html', {'aspirant': aspirant})

def check_aspirant_profile_status(request, uuid):
    aspirant = get_object_or_404(AspirantRegistration, uuid=uuid)
    if aspirant.profile_pdf:
        return render(request, 'aspirants/partials/profile_ready.html', {'aspirant': aspirant})
    return render(request, 'aspirants/partials/profile_status.html', {'aspirant': aspirant})

@staff_member_required
def download_aspirants_list_pdf(request):
    """Trigger async generation of full aspirants report."""
    from core.models import PartyReport
    from .tasks import generate_aspirants_report_pdf_task
    
    report = PartyReport.objects.create(
        report_type='aspirants_list',
        created_by=request.user
    )
    
    generate_aspirants_report_pdf_task.delay(report.id)
    
    return render(request, 'aspirants/report_processing.html', {'report': report})

def check_aspirant_report_status(request, report_id):
    from core.models import PartyReport
    report = get_object_or_404(PartyReport, id=report_id)
    if report.pdf_file:
        return render(request, 'aspirants/partials/report_ready.html', {'report': report})
    return render(request, 'aspirants/partials/report_status.html', {'report': report})

def role_detail(request, slug):
    """Detail view for leadership roles"""
    role = get_object_or_404(LeadershipRole, slug=slug)
    return render(request, 'aspirants/role_detail.html', {'role': role})
