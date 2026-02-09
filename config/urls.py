"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin

from django.urls import path, re_path, include
from django.views.static import serve
from django.views.generic import TemplateView

# Placed here to ensure AppRegistry is ready
import django
# -------------------------------------------------------------

from core import views as core_views
from users import views as user_views
from finance import views as finance_views
from aspirants import views as aspirants_views

urlpatterns = [
    # PWA (Keep outside i18n)
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw.js'),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/manifest+json'), name='manifest.json'),
]

urlpatterns += [
    path('admin/', admin.site.urls),
    
    # Core
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('manifesto-list/', core_views.manifesto_list, name='manifesto_list'),
    
    # Users
    path('join/', user_views.join, name='join'),
    path('join-coordinator/', user_views.join_coordinator, name='join_coordinator'),
    path('join/success/', user_views.join_success, name='join_success'),
    path('member/<int:member_id>/card/', user_views.download_card, name='download_card'),
    path('check-id/', user_views.check_id_number, name='check_id'),
    path('seed-members-cloud/', user_views.seed_members_view, name='seed_members_cloud'),
    
    # Finance
    path('donate/', finance_views.donate, name='donate'),
    
    # Navigation
    path('manifesto/', core_views.manifesto, name='manifesto'),
    path('manifesto/<str:slug>/', core_views.manifesto_detail, name='manifesto_detail'),
    path('manifesto/marijuana/country/<slug:country_slug>/', core_views.cannabis_country_detail, name='cannabis_country_detail'),
    path('gallery/', core_views.gallery, name='gallery'),
    path('leader/<slug:slug>/', core_views.leader_detail, name='leader_detail'),
    path('events/', core_views.events, name='events'),
    path('roles/<slug:slug>/', aspirants_views.role_detail, name='role_detail'),
    path('events/<int:event_id>/gate-pass/', core_views.download_gate_pass, name='download_gate_pass'),
    path('shop/', include('commerce.urls')),
    path('resources/', core_views.resources, name='resources'),
    path('analytics/', core_views.dashboard, name='dashboard'),
    path('contact/', core_views.contact, name='contact'),
    path('subscribe/', core_views.subscribe, name='subscribe'),
    
    # Blog/News
    path('news/', core_views.blog_list, name='blog_list'),
    path('news/<slug:slug>/', core_views.blog_detail, name='blog_detail'),
    
    # Counties
    path('counties/', core_views.counties, name='counties'),
    path('counties/map/', core_views.county_map, name='county_map'),
    path('counties/<slug:slug>/', core_views.county_detail, name='county_detail'),
    # Aspirants App
    path('aspirants/', include('aspirants.urls')),

    
    # Legal Pages
    path('privacy-policy/', core_views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', core_views.terms_of_service, name='terms_of_service'),
    path('cookie-policy/', core_views.cookie_policy, name='cookie_policy'),
    # API with versioning
    path('api/v1/', include('core.api.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

# API Documentation
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns += [
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif not os.environ.get('GS_BUCKET_NAME'):
    # Serve media files on Cloud Run manually ONLY if not using GCS
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
