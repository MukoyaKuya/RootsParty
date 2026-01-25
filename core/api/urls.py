from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaderViewSet, EventViewSet, ManifestoItemViewSet

# API versioning is handled in the main urls.py with /api/v1/ prefix
router = DefaultRouter()
router.register(r'leaders', LeaderViewSet, basename='leader')
router.register(r'events', EventViewSet, basename='event')
router.register(r'manifesto', ManifestoItemViewSet, basename='manifesto')

urlpatterns = [
    path('', include(router.urls)),
]
