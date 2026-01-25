# Standard library imports
import io
import os
import random
import string

# Third-party imports
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader, simpleSplit

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Sum, Count, Case, When, Value, IntegerField, F, Prefetch, Q
from django.http import FileResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from asgiref.sync import sync_to_async

# Local imports
from .forms import ContactForm, NewsletterForm
from .models import (
    Leader, ManifestoItem, ManifestoEvidence, BlogPost, County, PageContent, 
    HomeVideo, GatePass, LeadershipRole, CarouselImage, FloatingImage,
    GalleryPost, Event, Product, Resource, Vendor, ContactMessage, 
    NewsletterSubscriber, Constituency, Aspirant
)
from users.models import Member
from finance.models import Donation


def home(request):
    # Try to get stats from cache
    stats = cache.get('home_stats')
    if not stats:
        stats = {
            'member_count': Member.objects.count(),
            'total_counties': County.objects.count(),
            'active_counties': County.objects.filter(presence_status='active').count(),
            'growing_counties': County.objects.filter(presence_status='growing').count(),
        }
        cache.set('home_stats', stats, 300) # Cache for 5 minutes

    # Featured blog posts (keep real-time or short cache)
    featured_posts = BlogPost.objects.filter(is_published=True, is_featured=True)[:3]
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    
    # Get active home video
    video = HomeVideo.objects.filter(is_active=True).order_by('-created_at').first()
    
    # Get active carousel images
    carousel_images = CarouselImage.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # Get active floating hero image
    floating_image = FloatingImage.objects.filter(is_active=True, position='hero_right').first()

    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'video': video,
        'party_video': video,  # For the party video section
        'carousel_images': carousel_images,
        'floating_image': floating_image,
        # site_settings is automatically available via context processor
        **stats
    }
    
    return render(request, 'core/home.html', context)


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


def manifesto_detail(request, slug):
    item = get_object_or_404(ManifestoItem, slug=slug)
    return render(request, 'core/manifesto_detail.html', {'item': item})


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


def events(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    past_events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    return render(request, 'core/events.html', {'upcoming_events': upcoming_events, 'past_events': past_events})

def download_gate_pass(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Helper for wrapping text
    def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, leading=None):
        if leading is None:
            leading = font_size * 1.2
        c.setFont(font_name, font_size)
        from reportlab.lib.utils import simpleSplit
        lines = simpleSplit(text, font_name, font_size, max_width)
        for line in lines:
            c.drawCentredString(x, y, line)
            y -= leading
        return y # Return new Y position

    # 1. Background / Border
    p.setStrokeColor(colors.black)
    p.setLineWidth(5)
    p.rect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch)
    
    # 2. Header
    current_y = height - 1.0 * inch  # Moved up from 1.2
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(width/2, current_y, "ROOTS PARTY")
    
    current_y -= 0.35 * inch
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, current_y, "TINGIZA MTI!")
    
    # 3. Logo
    current_y -= 1.8 * inch # Reduced from 2.2 to save space
    logo_size = 1.6 * inch  # Slightly smaller logo
    logo_y = current_y + 0.1 * inch
    
    try:
        # Use first static dir
        logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'roots_logo_circle.png')
        if os.path.exists(logo_path):
             logo_x = (width - logo_size) / 2
             p.drawImage(logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)
    except Exception as e:
        print(f"Error loading logo: {e}")

    # 4. "OFFICIAL GATE PASS"
    current_y -= 0.6 * inch # Reduced from 0.8
    p.setFillColor(colors.red)
    p.setFont("Helvetica-Bold", 28) # Slightly smaller font
    p.drawCentredString(width/2, current_y, "OFFICIAL GATE PASS")
    
    # 5. Event Details
    current_y -= 0.8 * inch # Reduced from 1.0
    p.setFillColor(colors.black)
    # Wrap title if long
    current_y = draw_wrapped_text(p, event.title.upper(), width/2, current_y, width - 2*inch, "Helvetica-Bold", 22) # Font 24 -> 22
    
    current_y -= 0.5 * inch # Reduced from 0.6
    p.setFont("Helvetica", 16) # Font 18 -> 16
    p.drawCentredString(width/2, current_y, f"LOCATION: {event.location.upper()}")
    
    current_y -= 0.35 * inch # Reduced from 0.4
    p.drawCentredString(width/2, current_y, f"DATE: {event.date.strftime('%d %B %Y').upper()}")
    
    current_y -= 0.3 * inch
    p.drawCentredString(width/2, current_y, f"TIME: {event.date.strftime('%H:%M')}")
    
    # 6. Access Code
    current_y -= 0.8 * inch
    # Generate unique code and save
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    GatePass.objects.create(event=event, code=code)
    
    # Increment download count atomically (keeps for stats)
    from django.db.models import F
    Event.objects.filter(pk=event.pk).update(gate_pass_downloads=F('gate_pass_downloads') + 1)
    
    p.setFont("Courier-Bold", 24)
    p.setFillColor(colors.HexColor('#1a1a1a'))
    p.drawCentredString(width/2, current_y, f"CODE: {code}")

    # 7. QR Code
    qr_size = 2.4 * inch
    qr_y = 1.6 * inch 
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr_data = f"ROOTSPARTY-EVENT-{event.id}-{code}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = io.BytesIO()
    img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    p.drawImage(ImageReader(qr_buffer), (width - qr_size)/2, qr_y, width=qr_size, height=qr_size)

    # Footer
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(width/2, 1.0*inch, "Admit One. Non-Transferable. Tingiza Mti.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'gate_pass_{event.slug}.pdf')

 
def shop(request):
    """List all active vendors (shops)"""
    vendors = Vendor.objects.filter(is_active=True).prefetch_related('products')
    return render(request, 'core/shop_list.html', {'vendors': vendors})

def vendor_detail(request, vendor_slug):
    """Show a specific vendor's shop with their products"""
    vendor = get_object_or_404(Vendor, slug=vendor_slug, is_active=True)
    products = vendor.products.filter(is_available=True)
    return render(request, 'core/vendor_detail.html', {
        'vendor': vendor,
        'products': products
    })

def product_detail(request, vendor_slug, product_slug):
    """Show detailed product information"""
    vendor = get_object_or_404(Vendor, slug=vendor_slug, is_active=True)
    product = get_object_or_404(Product, slug=product_slug, vendor=vendor, is_available=True)
    return render(request, 'core/product_detail.html', {
        'vendor': vendor,
        'product': product
    })

def resources(request):
    docs = Resource.objects.filter(is_public=True)
    return render(request, 'core/resources.html', {'docs': docs})


@staff_member_required
def dashboard(request):
    # Try to get stats from cache
    dashboard_stats = cache.get('dashboard_stats')
    
    if not dashboard_stats:
        # --- MEMBERSHIP STATS ---
        # Total Members (excluding coordinators for this count if desired, or total people)
        # Let's count actual members distinct from coordinator applicants if they are mutually exclusive in intent
        total_members = Member.objects.filter(is_coordinator_applicant=False).count()
        total_coordinators = Member.objects.filter(is_coordinator_applicant=True).count()
        
        # Growth Stats
        today = timezone.now().date()
        week_ago = today - timezone.timedelta(days=7)
        
        new_members_today = Member.objects.filter(created_at__date=today, is_coordinator_applicant=False).count()
        new_members_week = Member.objects.filter(created_at__date__gte=week_ago, is_coordinator_applicant=False).count()
        
        # --- FINANCIALS ---
        total_donations_amount = Donation.objects.filter(status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
        # Note: In real app, we filter by 'COMPLETED'. Using PENDING for mock data visibility.
        
        upcoming_events_count = Event.objects.filter(date__gte=timezone.now()).count()
        
        dashboard_stats = {
            'total_members': total_members,
            'total_coordinators': total_coordinators,
            'new_members_today': new_members_today,
            'new_members_week': new_members_week,
            'total_donations_amount': total_donations_amount,
            'upcoming_events_count': upcoming_events_count,
        }
        # Cache for 15 minutes
        cache.set('dashboard_stats', dashboard_stats, 60 * 15)
    
    recent_members = Member.objects.filter(is_coordinator_applicant=False).order_by('-created_at')[:5]
    recent_donations = Donation.objects.order_by('-created_at')[:5]
    
    context = {
        **dashboard_stats,
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


async def contact(request):
    """Contact form view (Async)"""
    success = False
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        # Form validation touches DB if unique checks exist, so wrap it just in case
        is_valid = await sync_to_async(form.is_valid)()
        
        if is_valid:
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')
            subject_choice = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']
            
            # Save to database (Async)
            await sync_to_async(ContactMessage.objects.create)(
                name=name,
                email=email,
                phone=phone,
                subject=subject_choice,
                message=message_text
            )
            
            # Send email notification (Async)
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
                await sync_to_async(send_mail)(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else email,
                    [settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'info@rootsparty.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            success = True
            form = ContactForm()  # Reset form
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {
        'form': form,
        'success': success
    })



def subscribe(request):
    """Newsletter subscription view (HTMX)"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if likely spam/bot (simple check)
            if 'rootsparty' in email and 'admin' in email:
                 # Minimal honeypot-like logic could go here
                 pass
            
            # Save if not exists
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            
            if created:
                # Send notification to Admin
                try:
                    send_mail(
                        subject=f"[Roots Party Newsletter] New Subscriber: {email}",
                        message=f"New newsletter subscriber from website:\n\nEmail: {email}\n\nDate: {timezone.now()}",
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@rootsparty.co.ke',
                        recipient_list=[settings.CONTACT_EMAIL if hasattr(settings, 'CONTACT_EMAIL') else 'info@rootsparty.co.ke'],
                        fail_silently=True,
                    )
                except Exception:
                    pass
                
                return render(request, 'partials/subscribe_success.html', {'message': 'Subscribed successfully!'})
            else:
                return render(request, 'partials/subscribe_success.html', {'message': 'Already subscribed!'})
        else:
            return render(request, 'partials/subscribe_error.html', {'form': form})
    
    return HttpResponseNotAllowed(['POST'])


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
    
    # Increment view count atomically to prevent race conditions
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)
    
    # Related posts (same category)
    related_posts = BlogPost.objects.filter(
        is_published=True, 
        category=post.category
    ).exclude(id=post.id)[:3]
    
    return render(request, 'core/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })



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
    
    # Page Content
    try:
        page_content = PageContent.objects.get(page_name='counties')
    except PageContent.DoesNotExist:
        page_content = None
    
    # Cache stats
    stats = cache.get('counties_stats')
    if not stats:
        stats = {
            'total': all_counties.count(),
            'active': all_counties.filter(presence_status='active').count(),
            'growing': all_counties.filter(presence_status='growing').count(),
            'starting': all_counties.filter(presence_status='starting').count(),
            'planned': all_counties.filter(presence_status='planned').count(),
            'total_members': Member.objects.count(),
        }
        cache.set('counties_stats', stats, 300)

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

def role_detail(request, slug):
    """Detail view for leadership roles"""
    # Fetch from database
    role = get_object_or_404(LeadershipRole, slug=slug)
    return render(request, 'core/role_detail.html', {'role': role})

def privacy_policy(request):
    """View for Privacy Policy"""
    return render(request, 'core/privacy_policy.html')

def terms_of_service(request):
    """View for Terms of Service"""
    return render(request, 'core/terms_of_service.html')

def cookie_policy(request):
    """View for Cookie Policy"""
    return render(request, 'core/cookie_policy.html')


def mp_list(request):
    """List of counties for MP selection"""
    # Only show counties that have constituencies populated
    
    # Annotate with count of active MP aspirants
    counties = County.objects.annotate(
        c_count=Count('constituencies', distinct=True),
        aspirant_count=Count('aspirants', filter=Q(aspirants__is_active=True, aspirants__role='mp'), distinct=True)
    ).filter(c_count__gt=0).order_by('name')
    
    return render(request, 'core/mp_list.html', {'counties': counties})

def mp_county_detail(request, slug):
    """List constituencies in a county"""
    county = get_object_or_404(County, slug=slug)
    
    # Prefetch active MP candidates
    active_mps = Aspirant.objects.filter(is_active=True, role='mp')
    constituencies = county.constituencies.prefetch_related(
        Prefetch('aspirants', queryset=active_mps, to_attr='active_mps')
    ).order_by('name')
    
    return render(request, 'core/mp_county_detail.html', {
        'county': county,
        'constituencies': constituencies
    })

def mp_candidate_detail(request, constituency_slug):
    """Detail view for MP Candidate (Now Aspirant type MP)"""
    constituency = get_object_or_404(Constituency, slug=constituency_slug)
    # Get the active MP aspirant
    candidate = Aspirant.objects.filter(constituency=constituency, role='mp', is_active=True).first()
    
    return render(request, 'core/mp_candidate_detail.html', {
        'constituency': constituency,
        'candidate': candidate
    })

def aspirant_list(request):
    """List all aspirants with filtering"""
    role = request.GET.get('role', 'all')
    aspirants = Aspirant.objects.filter(is_active=True)
    
    if role != 'all':
        aspirants = aspirants.filter(role=role)
        
    # Order by role priority then name
    # We can't easily order by choice display, so we rely on model ordering
    
    return render(request, 'core/aspirant_list.html', {
        'aspirants': aspirants,
        'current_role': role
    })

def aspirant_detail(request, aspirant_id):
    """Generic detail view for any aspirant"""
    aspirant = get_object_or_404(Aspirant, id=aspirant_id)
    return render(request, 'core/aspirant_detail.html', {'aspirant': aspirant})

def dashboard_callback(request, context):
    """
    Callback to provide custom context to the Unfold admin dashboard.
    """
    from .models import Event, ContactMessage
    from users.models import Member
    from finance.models import Donation
    from django.db.models import Sum

    # Calculate stats
    total_members = Member.objects.count()
    total_donations = Donation.objects.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context.update({
        "custom_title": "Roots Party Control Panel",
        "kpi": [
            {
                "title": "Total Members",
                "metric": f"{total_members:,}",
                "footer": "Registered members",
                "icon": "groups",
            },
            {
                "title": "Total Donations",
                "metric": f"KES {total_donations:,.0f}",
                "footer": "Completed transactions",
                "icon": "payments",
            },
             {
                "title": "Upcoming Events",
                "metric": upcoming_events,
                "footer": "Scheduled rallies & meetings",
                "icon": "event",
            },
            {
                "title": "Unread Messages",
                "metric": unread_messages,
                "footer": "Inbox",
                "icon": "mark_email_unread",
            },
        ]
    })
    return context

