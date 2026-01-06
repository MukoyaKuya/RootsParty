from .models import Leader, ManifestoItem, ManifestoEvidence, BlogPost, County, PageContent
from users.models import Member

def home(request):
    # Member count
    member_count = Member.objects.count()
    
    # Featured blog posts
    featured_posts = BlogPost.objects.filter(is_published=True, is_featured=True)[:3]
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    
    # County stats
    total_counties = County.objects.count()
    active_counties = County.objects.filter(presence_status='active').count()
    growing_counties = County.objects.filter(presence_status='growing').count()
    
    return render(request, 'core/home.html', {
        'member_count': member_count,
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'total_counties': total_counties,
        'active_counties': active_counties,
        'growing_counties': growing_counties,
    })

def about(request):
    leaders = Leader.objects.all()
    
    # Stats for About page
    # Try to get PageContent for 'about'
    try:
        page_content = PageContent.objects.get(page_name='about')
        # Use KPI override if set, otherwise use DB count
        if page_content.kpi_value is not None:
            member_count = page_content.kpi_value
        else:
            member_count = Member.objects.count()
    except PageContent.DoesNotExist:
        page_content = None
        member_count = Member.objects.count()

    total_counties = County.objects.count()
    active_counties = County.objects.filter(presence_status='active').count()
    
    return render(request, 'core/about.html', {
        'leaders': leaders,
        'member_count': member_count,
        'total_counties': total_counties,
        'active_counties': active_counties,
        'page_content': page_content,
    })

def manifesto(request):
    items = ManifestoItem.objects.all()
    return render(request, 'core/manifesto.html', {'items': items})

from django.shortcuts import render, get_object_or_404

def manifesto_detail(request, slug):
    item = get_object_or_404(ManifestoItem, slug=slug)
    return render(request, 'core/manifesto_detail.html', {'item': item})

from .models import GalleryPost
def gallery(request):
    posts = GalleryPost.objects.prefetch_related('images').all()
    return render(request, 'core/gallery.html', {'posts': posts})

def leader_detail(request, slug):
    leader = get_object_or_404(Leader, slug=slug)
    return render(request, 'core/leader_detail.html', {'leader': leader})

def manifesto_list(request):
    commandments = [
        "Legalize Marijuana for Export",
        "Rearing Snakes for Venom Export",
        "Exporting Hyena Meat",
        "Hang the Corrupt",
        "Shut Down SGR",
        "4-Day Work Week",
        "Suspend the Constitution",
        "Move Capital to Isiolo",
        "Create 8 States",
        "Deport Idle Foreigners"
    ]
    return render(request, 'partials/manifesto_list.html', {'commandments': commandments})

from .models import Event
from django.utils import timezone

def events(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    past_events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    return render(request, 'core/events.html', {'upcoming_events': upcoming_events, 'past_events': past_events})

from .models import Product, Resource
 
def shop(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'core/shop.html', {'products': products})

def resources(request):
    docs = Resource.objects.filter(is_public=True)
    return render(request, 'core/resources.html', {'docs': docs})

from django.contrib.admin.views.decorators import staff_member_required
from users.models import Member
from finance.models import Donation
from django.db.models import Sum

@staff_member_required
def dashboard(request):
    # Stats
    total_members = Member.objects.count()
    total_donations_amount = Donation.objects.filter(status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
    # Note: In real app, we filter by 'COMPLETED'. Using PENDING for mock data visibility.
    
    upcoming_events_count = Event.objects.filter(date__gte=timezone.now()).count()
    
    recent_members = Member.objects.order_by('-created_at')[:5]
    recent_donations = Donation.objects.order_by('-created_at')[:5]
    
    context = {
        'total_members': total_members,
        'total_donations_amount': total_donations_amount,
        'upcoming_events_count': upcoming_events_count,
        'recent_members': recent_members,
        'recent_donations': recent_donations,
    }
    return render(request, 'core/dashboard.html', context)

def cannabis_country_detail(request, country_slug):
    """View for detailed cannabis legalization history by country"""
    evidence = get_object_or_404(ManifestoEvidence, slug=country_slug)
    # Get other countries for navigation
    other_countries = ManifestoEvidence.objects.filter(
        item__slug='marijuana'
    ).exclude(slug=country_slug)[:6]
    return render(request, 'core/cannabis_country_detail.html', {
        'evidence': evidence,
        'other_countries': other_countries
    })

from .forms import ContactForm
from .models import ContactMessage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def contact(request):
    """Contact form view"""
    success = False
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')
            subject_choice = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']
            
            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject_choice,
                message=message_text
            )
            
            # Also try to send email notification
            subject_display = dict(form.fields['subject'].choices).get(subject_choice, subject_choice)
            email_subject = f"[Roots Party Contact] {subject_display} - from {name}"
            email_body = f"""
New contact form submission from Roots Party website:

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject_display}

Message:
{message_text}

---
This message was sent from the Roots Party website contact form.
View all messages at: /admin/core/contactmessage/
            """
            
            try:
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else email,
                    [settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'info@rootsparty.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass  # Silently fail if email not configured
            
            success = True
            form = ContactForm()  # Reset form
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {
        'form': form,
        'success': success
    })


def blog_list(request):
    """List all published blog posts"""
    category = request.GET.get('category')
    
    posts = BlogPost.objects.filter(is_published=True)
    
    if category:
        posts = posts.filter(category=category)
    
    # Get all categories for filter
    categories = BlogPost.CATEGORY_CHOICES
    
    return render(request, 'core/blog_list.html', {
        'posts': posts,
        'categories': categories,
        'current_category': category,
    })


def blog_detail(request, slug):
    """View single blog post"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])
    
    # Related posts (same category)
    related_posts = BlogPost.objects.filter(
        is_published=True, 
        category=post.category
    ).exclude(id=post.id)[:3]
    
    return render(request, 'core/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })


from django.db.models import Case, When, Value, IntegerField

def counties(request):
    """View county presence map"""
    # Order: Active -> Growing -> Starting -> Planned
    all_counties = County.objects.annotate(
        status_order=Case(
            When(presence_status='active', then=Value(1)),
            When(presence_status='growing', then=Value(2)),
            When(presence_status='starting', then=Value(3)),
            When(presence_status='planned', then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-members_count', 'name')
    
    # Stats
    stats = {
        'total': all_counties.count(),
        'active': all_counties.filter(presence_status='active').count(),
        'growing': all_counties.filter(presence_status='growing').count(),
        'starting': all_counties.filter(presence_status='starting').count(),
        'planned': all_counties.filter(presence_status='planned').count(),
        'total_members': sum(c.members_count for c in all_counties),
    }
    
    # Page Content
    try:
        page_content = PageContent.objects.get(page_name='counties')
    except PageContent.DoesNotExist:
        page_content = None
    
    return render(request, 'core/counties.html', {
        'counties': all_counties,
        'stats': stats,
        'page_content': page_content,
    })


def county_map(request):
    """View interactive map of counties"""
    # Send all counties data for the map to consume
    counties_data = list(County.objects.all().values('name', 'presence_status', 'members_count', 'slug'))
    
    return render(request, 'core/county_map.html', {
        'counties_json': counties_data
    })


def county_detail(request, slug):
    """Detail view for a specific county"""
    county = get_object_or_404(County, slug=slug)
    return render(request, 'core/county_detail.html', {'county': county})
