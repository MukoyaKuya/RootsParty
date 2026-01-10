from .models import Leader, ManifestoItem, ManifestoEvidence, BlogPost, County, PageContent, HomeVideo, GatePass
from users.models import Member
from django.core.cache import cache

import io
import os
import random
import string
import qrcode
from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

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
    


    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'video': video,
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
    
    # Increment download count (keep for stats)
    event.gate_pass_downloads += 1
    event.save(update_fields=['gate_pass_downloads'])
    
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
