from .models import Leader, ManifestoItem

def home(request):
    return render(request, 'core/home.html')

def about(request):
    leaders = Leader.objects.all()
    return render(request, 'core/about.html', {'leaders': leaders})

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

