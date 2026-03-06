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
    from ..cache_utils import get_dashboard_kpi_for_admin

    context.update({
        "custom_title": "Roots Party Control Panel",
        "kpi": get_dashboard_kpi_for_admin(),
    })
    return context
