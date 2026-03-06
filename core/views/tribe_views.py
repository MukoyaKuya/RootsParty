"""
Tribe-related views: tribes list and tribe detail.
"""
from django.shortcuts import render, get_object_or_404

from ..models import Tribe


def tribes(request):
    tribes_qs = Tribe.objects.all().order_by('order')
    return render(request, 'core/tribes.html', {'tribes': tribes_qs})


def tribe_detail(request, slug):
    tribe = get_object_or_404(Tribe, slug=slug)
    return render(request, 'core/tribe_detail.html', {'tribe': tribe})
