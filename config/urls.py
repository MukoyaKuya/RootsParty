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
from django.contrib import admin
from django.urls import path
from core import views as core_views
from users import views as user_views
from finance import views as finance_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('manifesto-list/', core_views.manifesto_list, name='manifesto_list'),
    
    # Users
    path('join/', user_views.join, name='join'),
    path('check-id/', user_views.check_id_number, name='check_id'),
    
    # Finance
    path('donate/', finance_views.donate, name='donate'),
    
    # Navigation
    path('manifesto/', core_views.manifesto, name='manifesto'),
    path('manifesto/<str:slug>/', core_views.manifesto_detail, name='manifesto_detail'),
    path('manifesto/marijuana/country/<slug:country_slug>/', core_views.cannabis_country_detail, name='cannabis_country_detail'),
    path('gallery/', core_views.gallery, name='gallery'),
    path('leader/<slug:slug>/', core_views.leader_detail, name='leader_detail'),
    path('events/', core_views.events, name='events'),
    path('shop/', core_views.shop, name='shop'),
    path('resources/', core_views.resources, name='resources'),
    path('analytics/', core_views.dashboard, name='dashboard'),
    path('contact/', core_views.contact, name='contact'),
    
    # Blog/News
    path('news/', core_views.blog_list, name='blog_list'),
    path('news/<slug:slug>/', core_views.blog_detail, name='blog_detail'),
    
    # Counties
    path('counties/', core_views.counties, name='counties'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
