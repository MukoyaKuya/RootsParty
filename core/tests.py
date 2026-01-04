from django.test import TestCase
from .models import Product, Event, Leader
from django.utils import timezone

class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name="Test Shirt",
            price=1000,
            description="A test shirt"
        )
        self.assertEqual(product.slug, "test-shirt")
        self.assertTrue(product.is_available)

class EventModelTest(TestCase):
    def test_create_event(self):
        event = Event.objects.create(
            title="Test Rally",
            location="Nairobi",
            date=timezone.now()
        )
        self.assertEqual(event.slug, "test-rally")
        
class LeaderModelTest(TestCase):
    def test_create_leader(self):
        leader = Leader.objects.create(
            name="John Doe",
            role="Chairman"
        )
        self.assertEqual(leader.slug, "john-doe")
