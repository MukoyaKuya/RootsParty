from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Event, Leader, ManifestoItem
from django.utils import timezone
import datetime

class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Setup data
        self.leader = Leader.objects.create(name="Test Leader", role="Test Role", slug="test-leader")
        self.item = ManifestoItem.objects.create(title="Legalize It", slug="legalize-it", icon="🌿")
        self.event = Event.objects.create(
            title="Nairobi Rally", 
            location="Nairobi", 
            date=timezone.now() + datetime.timedelta(days=1),
            slug="nairobi-rally"
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_manifesto_page(self):
        response = self.client.get(reverse('manifesto'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Legalize It")

    def test_leader_detail(self):
        url = reverse('leader_detail', args=[self.leader.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Leader")

    def test_events_page(self):
        response = self.client.get(reverse('events'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nairobi Rally")

class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name="Test Shirt",
            price=1000,
            description="A test shirt"
        )
        self.assertEqual(product.slug, "test-shirt")
        self.assertTrue(product.is_available)

class CoreAPITest(TestCase):
    def test_leader_api(self):
        Leader.objects.create(name="API Leader", role="API Role")
        response = self.client.get('/api/v1/leaders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API Leader")
