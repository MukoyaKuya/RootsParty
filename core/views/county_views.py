"""
County-related views: counties list, map, and county detail.
"""
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import render, get_object_or_404

from users.models import Member

from ..models import County, PageContent


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
