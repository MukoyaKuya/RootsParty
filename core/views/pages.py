"""
Public page views: home, about, manifesto, gallery, shop, blog, counties, legal, etc.
"""
import random
import string

from django.core.cache import cache
from django.db.models import Case, When, Value, IntegerField, F
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import cache_page

from ..models import (
    Leader, ManifestoItem, ManifestoEvidence, BlogPost, County, PageContent,
    HomeVideo, GatePass, CarouselImage, FloatingImage,
    GalleryPost, Event, Resource,
)
from ..services.pdf import build_gate_pass_pdf
from users.models import Member


@cache_page(60 * 15)
def home(request):
    stats = cache.get('home:stats:v1')
    if not stats:
        stats = {
            'member_count': Member.objects.count(),
            'total_counties': County.objects.count(),
            'active_counties': County.objects.filter(presence_status='active').count(),
            'growing_counties': County.objects.filter(presence_status='growing').count(),
        }
        cache.set('home:stats:v1', stats, 300)

    featured_posts = BlogPost.objects.filter(is_published=True, is_featured=True)[:3]
    latest_posts = BlogPost.objects.filter(is_published=True)[:3]
    video = HomeVideo.objects.filter(is_active=True).order_by('-created_at').first()
    carousel_images = CarouselImage.objects.filter(is_active=True).order_by('order', '-created_at')
    floating_image = FloatingImage.objects.filter(is_active=True, position='hero_right').first()

    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'video': video,
        'party_video': video,
        'carousel_images': carousel_images,
        'floating_image': floating_image,
        **stats
    }
    return render(request, 'core/home.html', context)


def about(request):
    leaders = Leader.objects.all()
    try:
        page_content = PageContent.objects.get(page_name='about')
        member_count = page_content.kpi_value if page_content.kpi_value is not None else Member.objects.count()
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


@cache_page(60 * 60)
def manifesto(request):
    items = ManifestoItem.objects.all()
    return render(request, 'core/manifesto.html', {'items': items})


def manifesto_detail(request, slug):
    item = get_object_or_404(ManifestoItem, slug=slug)
    return render(request, 'core/manifesto_detail.html', {'item': item})


@cache_page(60 * 20)
def gallery(request):
    posts = GalleryPost.objects.prefetch_related('images').all()
    return render(request, 'core/gallery.html', {'posts': posts})


def leader_detail(request, slug):
    leader = get_object_or_404(Leader, slug=slug)
    return render(request, 'core/leader_detail.html', {'leader': leader})


def manifesto_list(request):
    commandments = list(ManifestoItem.objects.order_by('order').values_list('title', flat=True))
    # Fallback to hardcoded list if database is empty 
    if not commandments:
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
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    GatePass.objects.create(event=event, code=code)
    Event.objects.filter(pk=event.pk).update(gate_pass_downloads=F('gate_pass_downloads') + 1)
    buffer = build_gate_pass_pdf(event, code)
    return FileResponse(buffer, as_attachment=True, filename=f'gate_pass_{event.slug}.pdf')




def resources(request):
    docs = Resource.objects.filter(is_public=True)
    return render(request, 'core/resources.html', {'docs': docs})


def cannabis_country_detail(request, country_slug):
    evidence = get_object_or_404(ManifestoEvidence, slug=country_slug)
    other_countries = ManifestoEvidence.objects.filter(item__slug='marijuana').exclude(slug=country_slug)[:6]
    return render(request, 'core/cannabis_country_detail.html', {
        'evidence': evidence,
        'other_countries': other_countries
    })


@cache_page(60 * 10)
def blog_list(request):
    category = request.GET.get('category')
    posts = BlogPost.objects.filter(is_published=True)
    if category:
        posts = posts.filter(category=category)
    categories = BlogPost.CATEGORY_CHOICES
    return render(request, 'core/blog_list.html', {
        'posts': posts,
        'categories': categories,
        'current_category': category,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)
    related_posts = BlogPost.objects.filter(is_published=True, category=post.category).exclude(id=post.id)[:3]
    return render(request, 'core/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })


@cache_page(60 * 30)
def counties(request):
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

    try:
        page_content = PageContent.objects.get(page_name='counties')
    except PageContent.DoesNotExist:
        page_content = None

    stats = cache.get('counties:page_stats:v1')
    if not stats:
        stats = {
            'total': all_counties.count(),
            'active': all_counties.filter(presence_status='active').count(),
            'growing': all_counties.filter(presence_status='growing').count(),
            'starting': all_counties.filter(presence_status='starting').count(),
            'planned': all_counties.filter(presence_status='planned').count(),
            'total_members': Member.objects.count(),
        }
        cache.set('counties:page_stats:v1', stats, 300)

    return render(request, 'core/counties.html', {
        'counties': all_counties,
        'stats': stats,
        'page_content': page_content,
    })


def county_map(request):
    counties_data = list(County.objects.all().values('name', 'presence_status', 'members_count', 'slug'))
    return render(request, 'core/county_map.html', {'counties_json': counties_data})


def county_detail(request, slug):
    county = get_object_or_404(County, slug=slug)
    return render(request, 'core/county_detail.html', {'county': county})


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')


def cookie_policy(request):
    return render(request, 'core/cookie_policy.html')
