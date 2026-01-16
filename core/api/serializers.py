from rest_framework import serializers
from core.models import Leader, Event, ManifestoItem

class LeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leader
        fields = ['id', 'name', 'role', 'slug', 'image', 'bio', 'twitter_handle']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'location', 'date', 'slug', 'description', 'is_completed', 'image']

class ManifestoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManifestoItem
        fields = ['id', 'title', 'slug', 'icon', 'summary', 'description']
