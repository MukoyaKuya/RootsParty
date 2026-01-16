from rest_framework import viewsets
from core.models import Leader, Event, ManifestoItem
from .serializers import LeaderSerializer, EventSerializer, ManifestoItemSerializer

class LeaderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Leader.objects.all()
    serializer_class = LeaderSerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    filterset_fields = ['is_completed']

class ManifestoItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ManifestoItem.objects.all().order_by('order')
    serializer_class = ManifestoItemSerializer
