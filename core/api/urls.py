from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaderViewSet, EventViewSet, ManifestoItemViewSet

router = DefaultRouter()
router.register(r'leaders', LeaderViewSet)
router.register(r'events', EventViewSet)
router.register(r'manifesto', ManifestoItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
