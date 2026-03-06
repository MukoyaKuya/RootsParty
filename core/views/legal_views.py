"""
Legal and policy pages: privacy, terms, cookies, land, labour, dignity.
"""
from django.shortcuts import render


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')


def cookie_policy(request):
    return render(request, 'core/cookie_policy.html')


def land(request):
    return render(request, 'core/land.html')


def labour(request):
    return render(request, 'core/labour.html')


def dignity(request):
    return render(request, 'core/dignity.html')
