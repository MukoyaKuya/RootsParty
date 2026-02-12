from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from core.models import Leader, Event, ManifestoItem

class LeaderSerializer(serializers.ModelSerializer):
    """Serializer for Leader model."""
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Leader
        fields = ['uuid', 'name', 'role', 'slug', 'image', 'bio', 'twitter_handle', 'nickname', 'order']
        read_only_fields = ['uuid', 'slug']

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    is_upcoming = serializers.ReadOnlyField()
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Event
        fields = [
            'uuid', 'title', 'location', 'date', 'slug', 'description', 
            'is_completed', 'is_upcoming', 'image', 'gate_pass_downloads'
        ]
        read_only_fields = ['uuid', 'slug', 'is_upcoming', 'gate_pass_downloads']

class ManifestoItemSerializer(serializers.ModelSerializer):
    """Serializer for ManifestoItem model."""
    
    class Meta:
        model = ManifestoItem
        fields = [
            'uuid', 'title', 'slug', 'icon', 'summary', 'description', 
            'local_impact', 'target_revenue', 'order'
        ]
        read_only_fields = ['uuid', 'slug']
