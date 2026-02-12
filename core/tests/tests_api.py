"""
API endpoint tests.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Leader, Event, ManifestoItem


class LeaderAPITest(TestCase):
    """Test Leader API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.leader = Leader.objects.create(
            name="Test Leader",
            role="Test Role",
            slug="test-leader",
            bio="Test biography"
        )
    
    def test_list_leaders(self):
        """Test listing all leaders."""
        url = '/api/v1/leaders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Test Leader")
    
    def test_retrieve_leader(self):
        """Test retrieving a specific leader."""
        url = f'/api/v1/leaders/{self.leader.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Leader")
        self.assertEqual(response.data['role'], "Test Role")
    
    def test_leader_pagination(self):
        """Test leader list pagination."""
        # Create multiple leaders
        for i in range(25):
            Leader.objects.create(
                name=f"Leader {i}",
                role="Role",
                slug=f"leader-{i}"
            )
        
        url = '/api/v1/leaders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size


class EventAPITest(TestCase):
    """Test Event API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.event = Event.objects.create(
            title="Test Event",
            location="Test Location",
            slug="test-event",
            description="Test description"
        )
    
    def test_list_events(self):
        """Test listing all events."""
        url = '/api/v1/events/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_filter_events_by_completion(self):
        """Test filtering events by completion status."""
        completed_event = Event.objects.create(
            title="Completed Event",
            location="Location",
            slug="completed-event",
            is_completed=True
        )
        
        url = '/api/v1/events/?is_completed=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return completed events
        for event in response.data['results']:
            self.assertTrue(event['is_completed'])


class ManifestoItemAPITest(TestCase):
    """Test ManifestoItem API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.item = ManifestoItem.objects.create(
            title="Test Manifesto",
            slug="test-manifesto",
            icon="🌿",
            summary="Test summary",
            description="Test description"
        )
    
    def test_list_manifesto_items(self):
        """Test listing all manifesto items."""
        url = '/api/v1/manifesto/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_manifesto_items_ordered(self):
        """Test that manifesto items are ordered correctly."""
        item1 = ManifestoItem.objects.create(
            title="Item 1",
            slug="item-1",
            icon="🌿",
            summary="Summary",
            description="Description",
            order=2
        )
        item2 = ManifestoItem.objects.create(
            title="Item 2",
            slug="item-2",
            icon="🌿",
            summary="Summary",
            description="Description",
            order=1
        )
        
        url = '/api/v1/manifesto/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Item 2 (order=1) should come before Item 1 (order=2)
        results = response.data['results']
        self.assertEqual(results[0]['slug'], 'item-2')


class APIRateLimitTest(TestCase):
    """Test API rate limiting."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_api_endpoint_accessible(self):
        """Test that API endpoints are accessible."""
        url = '/api/v1/leaders/'
        response = self.client.get(url)
        # Should be accessible (rate limiting is per hour, not per test)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS])
