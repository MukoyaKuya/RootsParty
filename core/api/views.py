from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view
from core.models import Leader, Event, ManifestoItem
from core.utils.logging import log_api_request, get_logger
from .serializers import LeaderSerializer, EventSerializer, ManifestoItemSerializer

logger = get_logger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema_view(
    list=extend_schema(
        summary="List all leaders",
        description="Retrieve a paginated list of all party leaders."
    ),
    retrieve=extend_schema(
        summary="Get leader details",
        description="Retrieve detailed information about a specific leader."
    ),
)
class LeaderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing party leaders.
    
    Provides read-only access to leader information including
    name, role, biography, and social media handles.
    """
    queryset = Leader.objects.all()
    serializer_class = LeaderSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def list(self, request, *args, **kwargs):
        log_api_request('LeaderViewSet', 'list', request.user)
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        log_api_request('LeaderViewSet', 'retrieve', request.user)
        return super().retrieve(request, *args, **kwargs)

@extend_schema_view(
    list=extend_schema(
        summary="List all events",
        description="Retrieve a paginated list of party events. Can be filtered by completion status."
    ),
    retrieve=extend_schema(
        summary="Get event details",
        description="Retrieve detailed information about a specific event."
    ),
)
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing party events.
    
    Provides read-only access to event information including
    title, location, date, description, and gate pass downloads.
    """
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    filterset_fields = ['is_completed']
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def list(self, request, *args, **kwargs):
        log_api_request('EventViewSet', 'list', request.user)
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        log_api_request('EventViewSet', 'retrieve', request.user)
        return super().retrieve(request, *args, **kwargs)

@extend_schema_view(
    list=extend_schema(
        summary="List all manifesto items",
        description="Retrieve a paginated list of party manifesto items, ordered by priority."
    ),
    retrieve=extend_schema(
        summary="Get manifesto item details",
        description="Retrieve detailed information about a specific manifesto item."
    ),
)
class ManifestoItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing party manifesto items.
    
    Provides read-only access to manifesto information including
    title, summary, description, and local impact details.
    """
    queryset = ManifestoItem.objects.all().order_by('order')
    serializer_class = ManifestoItemSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def list(self, request, *args, **kwargs):
        log_api_request('ManifestoItemViewSet', 'list', request.user)
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        log_api_request('ManifestoItemViewSet', 'retrieve', request.user)
        return super().retrieve(request, *args, **kwargs)
