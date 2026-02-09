"""
Dashboard and admin dashboard callback views.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone

from ..cache_utils import get_dashboard_stats
from users.models import Member
from finance.models import Donation
from aspirants.models import AspirantRegistration


@staff_member_required
def dashboard(request):
    """Analytics dashboard; stats from cache, recent lists fresh."""
    dashboard_stats = get_dashboard_stats()
    recent_members = Member.objects.filter(is_coordinator_applicant=False).order_by('-created_at')[:5]
    recent_donations = Donation.objects.order_by('-created_at')[:5]
    recent_aspirants = AspirantRegistration.objects.order_by('-created_at')[:5]

    context = {
        **dashboard_stats,
        'recent_members': recent_members,
        'recent_donations': recent_donations,
        'recent_aspirants': recent_aspirants,
    }
    return render(request, 'core/dashboard.html', context)


def dashboard_callback(request, context):
    """Callback to provide custom context to the Unfold admin dashboard."""
    from ..models import ContactMessage
    
    # Use unified stats from cache_utils
    stats = get_dashboard_stats()
    
    # Unread messages (not currently in get_dashboard_stats)
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context.update({
        "custom_title": "Roots Party Control Panel",
        "kpi": [
            {"title": "Total Members", "metric": f"{stats['total_members'] + stats['total_coordinators']:,}", "footer": "Registered members", "icon": "groups"},
            {"title": "Total Donations", "metric": f"KES {stats['total_donations_amount']:,.0f}", "footer": "Completed transactions", "icon": "payments"},
            {"title": "Upcoming Events", "metric": stats['upcoming_events_count'], "footer": "Scheduled rallies & meetings", "icon": "event"},
            {"title": "Unread Messages", "metric": unread_messages, "footer": "Inbox", "icon": "mark_email_unread"},
        ]
    })
    return context
