"""
Cache utility functions for the Roots Party application.

Provides helper functions for caching expensive database queries
and managing cache invalidation.
"""

from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.utils import timezone
from typing import List, Dict, Any, Optional


def get_cached_aspirants(timeout: int = 300) -> List[Dict[str, Any]]:
    """
    Get all aspirants with county data - cached for 5 minutes.
    
    Args:
        timeout: Cache timeout in seconds (default: 300 = 5 minutes)
    
    Returns:
        List of aspirant dictionaries with county information
    """
    cache_key = 'aspirants:all:v1'
    result = cache.get(cache_key)
    
    if result is None:
        from aspirants.models import AspirantRegistration
        result = list(
            AspirantRegistration.objects
            .select_related('county')
            .values(
                'id', 'surname', 'other_names', 'position',
                'county__name', 'constituency', 'ward',
                'status', 'is_verified', 'created_at'
            )
            .order_by('-created_at')
        )
        cache.set(cache_key, result, timeout)
    
    return result


def get_cached_verified_aspirants(timeout: int = 600) -> List[Dict[str, Any]]:
    """
    Get verified aspirants only - cached for 10 minutes.
    
    Args:
        timeout: Cache timeout in seconds (default: 600 = 10 minutes)
    
    Returns:
        List of verified aspirant dictionaries
    """
    cache_key = 'aspirants:verified:v1'
    result = cache.get(cache_key)
    
    if result is None:
        from aspirants.models import AspirantRegistration
        result = list(
            AspirantRegistration.objects
            .filter(is_verified=True)
            .select_related('county')
            .values(
                'id', 'surname', 'other_names', 'position',
                'county__name', 'photo'
            )
            .order_by('position', 'county__name')
        )
        cache.set(cache_key, result, timeout)
    
    return result


def get_cached_county_stats(timeout: int = 600) -> List[Dict[str, Any]]:
    """
    Get county statistics with aspirant counts - cached for 10 minutes.
    
    Args:
        timeout: Cache timeout in seconds (default: 600 = 10 minutes)
    
    Returns:
        List of county dictionaries with statistics
    """
    cache_key = 'counties:stats:v1'
    result = cache.get(cache_key)
    
    if result is None:
        from core.models import County
        result = list(
            County.objects.annotate(
                aspirant_count=Count('aspirantregistration_set'),
                verified_count=Count('aspirantregistration_set', filter=Q(aspirantregistration_set__is_verified=True))
            ).values(
                'id', 'name', 'slug', 'capital',
                'aspirant_count', 'verified_count'
            ).order_by('name')
        )
        cache.set(cache_key, result, timeout)
    
    return result


def get_dashboard_stats(timeout: int = 900) -> Dict[str, Any]:
    """
    Get aggregated dashboard statistics (members, donations, events, aspirants).
    Cached for 15 minutes by default.

    Args:
        timeout: Cache timeout in seconds (default: 900 = 15 minutes)

    Returns:
        Dict with keys: total_members, total_coordinators, new_members_today,
        new_members_week, total_donations_amount, upcoming_events_count,
        total_aspirants, new_aspirants_today, new_aspirants_week, aspirants_by_position.
        Cache key: dashboard:stats:v1.
    """
    cache_key = 'dashboard:stats:v1'
    result = cache.get(cache_key)
    if result is not None:
        return result

    from users.models import Member
    from finance.models import Donation
    from core.models import Event
    from aspirants.models import AspirantRegistration

    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)

    total_members = Member.objects.filter(is_coordinator_applicant=False).count()
    total_coordinators = Member.objects.filter(is_coordinator_applicant=True).count()
    new_members_today = Member.objects.filter(created_at__date=today, is_coordinator_applicant=False).count()
    new_members_week = Member.objects.filter(created_at__date__gte=week_ago, is_coordinator_applicant=False).count()

    total_donations_amount = (
        Donation.objects.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    )
    upcoming_events_count = Event.objects.filter(date__gte=timezone.now()).count()

    total_aspirants = AspirantRegistration.objects.count()
    new_aspirants_today = AspirantRegistration.objects.filter(created_at__date=today).count()
    new_aspirants_week = AspirantRegistration.objects.filter(created_at__date__gte=week_ago).count()
    aspirants_by_position = list(
        AspirantRegistration.objects.values('position').annotate(count=Count('id')).order_by('-count')
    )

    result = {
        'total_members': total_members,
        'total_coordinators': total_coordinators,
        'new_members_today': new_members_today,
        'new_members_week': new_members_week,
        'total_donations_amount': total_donations_amount,
        'upcoming_events_count': upcoming_events_count,
        'total_aspirants': total_aspirants,
        'new_aspirants_today': new_aspirants_today,
        'new_aspirants_week': new_aspirants_week,
        'aspirants_by_position': aspirants_by_position,
    }
    cache.set(cache_key, result, timeout)
    return result


def get_cached_manifesto_items(timeout: int = 3600) -> List[Dict[str, Any]]:
    """
    Get all manifesto items - cached for 1 hour (rarely changes).
    
    Args:
        timeout: Cache timeout in seconds (default: 3600 = 1 hour)
    
    Returns:
        List of manifesto item dictionaries
    """
    cache_key = 'manifesto:items:v1'
    result = cache.get(cache_key)
    
    if result is None:
        from core.models import ManifestoItem
        result = list(
            ManifestoItem.objects.values(
                'id', 'title', 'slug', 'icon', 'summary',
                'local_impact', 'target_revenue', 'order'
            ).order_by('order')
        )
        cache.set(cache_key, result, timeout)
    
    return result


def get_cached_blog_posts(limit: int = 10, timeout: int = 600) -> List[Dict[str, Any]]:
    """
    Get recent blog posts - cached for 10 minutes.
    
    Args:
        limit: Number of posts to return
        timeout: Cache timeout in seconds (default: 600 = 10 minutes)
    
    Returns:
        List of blog post dictionaries
    """
    cache_key = f'blog:posts:latest:{limit}:v1'
    result = cache.get(cache_key)
    
    if result is None:
        from core.models import BlogPost
        result = list(
            BlogPost.objects
            .select_related('county')
            .values(
                'id', 'title', 'slug', 'excerpt', 'image',
                'county__name', 'created_at', 'is_featured'
            )
            .order_by('-created_at')[:limit]
        )
        cache.set(cache_key, result, timeout)
    
    return result


def get_cached_leaders(timeout: int = 1800) -> List[Dict[str, Any]]:
    """
    Get party leaders - cached for 30 minutes.
    
    Args:
        timeout: Cache timeout in seconds (default: 1800 = 30 minutes)
    
    Returns:
        List of leader dictionaries
    """
    cache_key = 'leaders:all:v1'
    result = cache.get(cache_key)
    
    if result is None:
        from core.models import Leader
        result = list(
            Leader.objects.values(
                'id', 'name', 'slug', 'position', 'bio',
                'image', 'twitter_handle', 'order'
            ).order_by('-order')
        )
        cache.set(cache_key, result, timeout)
    
    return result


def invalidate_aspirant_cache():
    """Clear all aspirant-related caches when data changes."""
    patterns = [
        'aspirants:*',
        'counties:stats:*',
        'counties:page_stats:*',
        'dashboard:stats:*',
        'home:stats:*',
    ]
    for pattern in patterns:
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            # Fallback for non-Redis cache backends
            cache.clear()
            break


def invalidate_content_cache():
    """Clear content-related caches (blog, manifesto, etc.)."""
    patterns = [
        'blog:*',
        'manifesto:*',
        'leaders:*',
    ]
    for pattern in patterns:
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            cache.clear()
            break


def invalidate_county_cache():
    """Clear county-related caches."""
    try:
        cache.delete_pattern('counties:*')
        cache.delete_pattern('dashboard:stats:*')
        cache.delete_pattern('home:stats:*')
    except AttributeError:
        cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get Redis cache statistics.
    
    Returns:
        Dictionary with cache statistics or empty dict if unavailable
    """
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')
        info = conn.info('stats')
        
        return {
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': calculate_hit_rate(
                info.get('keyspace_hits', 0),
                info.get('keyspace_misses', 0)
            ),
            'keys': conn.dbsize(),
            'memory_used': info.get('used_memory_human', 'N/A'),
        }
    except Exception:
        return {}


def calculate_hit_rate(hits: int, misses: int) -> str:
    """Calculate cache hit rate percentage."""
    total = hits + misses
    if total == 0:
        return '0%'
    return f'{(hits / total * 100):.1f}%'
