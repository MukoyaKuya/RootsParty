from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from core.models import Leader, Event, ManifestoItem
from .serializers import LeaderSerializer, EventSerializer, ManifestoItemSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class LeaderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Leader.objects.all()
    serializer_class = LeaderSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    filterset_fields = ['is_completed']
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

class ManifestoItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ManifestoItem.objects.all().order_by('order')
    serializer_class = ManifestoItemSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
