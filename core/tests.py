from django.test import TestCase, Client, AsyncClient
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Event, Leader, ManifestoItem, BlogPost, ContactMessage, NewsletterSubscriber
from django.utils import timezone
import datetime


class CoreViewsTest(TestCase):
    """Test cases for basic core views."""
    
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
    """Test cases for Product model."""
    
    def test_create_product(self):
        product = Product.objects.create(
            name="Test Shirt",
            price=1000,
            description="A test shirt"
        )
        self.assertEqual(product.slug, "test-shirt")
        self.assertTrue(product.is_available)


class CoreAPITest(TestCase):
    """Test cases for API endpoints."""
    
    def test_leader_api(self):
        Leader.objects.create(name="API Leader", role="API Role")
        response = self.client.get('/api/v1/leaders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API Leader")


class ContactViewTest(TestCase):
    """Test cases for the async contact form view."""
    
    def setUp(self):
        self.client = Client()
        self.contact_url = reverse('contact')
    
    def test_contact_page_loads(self):
        """Test that contact page loads correctly."""
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
    
    def test_contact_form_submission(self):
        """Test successful contact form submission."""
        initial_count = ContactMessage.objects.count()
        response = self.client.post(self.contact_url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '0712345678',
            'subject': 'membership',
            'message': 'This is a test message.'
        })
        self.assertEqual(response.status_code, 200)
        # Should create a contact message
        self.assertEqual(ContactMessage.objects.count(), initial_count + 1)
    
    def test_contact_form_invalid_email(self):
        """Test contact form with invalid email."""
        response = self.client.post(self.contact_url, {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'membership',
            'message': 'This is a test message.'
        })
        # Should still render the form (with errors)
        self.assertEqual(response.status_code, 200)
        # Should NOT create a message
        self.assertEqual(ContactMessage.objects.count(), 0)


class DashboardAuthorizationTest(TestCase):
    """Test cases for staff-only dashboard access."""
    
    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboard')
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123'
        )
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
            is_staff=True
        )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard redirects unauthenticated users."""
        response = self.client.get(self.dashboard_url)
        self.assertNotEqual(response.status_code, 200)
        # Should redirect to login
        self.assertIn('/admin/', response.url)
    
    def test_dashboard_requires_staff(self):
        """Test that non-staff users cannot access dashboard."""
        self.client.login(username='regularuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertNotEqual(response.status_code, 200)
    
    def test_dashboard_accessible_to_staff(self):
        """Test that staff users can access dashboard."""
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)


class NewsletterSubscribeTest(TestCase):
    """Test cases for newsletter subscription."""
    
    def setUp(self):
        self.client = Client()
        self.subscribe_url = reverse('subscribe')
    
    def test_subscribe_requires_post(self):
        """Test that GET request is not allowed."""
        response = self.client.get(self.subscribe_url)
        self.assertEqual(response.status_code, 405)
    
    def test_successful_subscription(self):
        """Test successful newsletter subscription."""
        response = self.client.post(self.subscribe_url, {
            'email': 'newsubscriber@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(NewsletterSubscriber.objects.filter(
            email='newsubscriber@example.com'
        ).exists())
    
    def test_duplicate_subscription(self):
        """Test that duplicate subscription is handled gracefully."""
        # Create existing subscriber
        NewsletterSubscriber.objects.create(email='existing@example.com')
        
        response = self.client.post(self.subscribe_url, {
            'email': 'existing@example.com'
        })
        self.assertEqual(response.status_code, 200)
        # Should still only have one subscriber
        self.assertEqual(
            NewsletterSubscriber.objects.filter(email='existing@example.com').count(),
            1
        )


class BlogViewsTest(TestCase):
    """Test cases for blog views and view counter."""
    
    def setUp(self):
        self.client = Client()
        self.post = BlogPost.objects.create(
            title="Test Blog Post",
            slug="test-blog-post",
            excerpt="Test excerpt",
            content="Test content",
            is_published=True
        )
    
    def test_blog_list_page(self):
        """Test blog list page loads."""
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Blog Post")
    
    def test_blog_detail_increments_views(self):
        """Test that viewing a blog post increments the view count."""
        initial_views = self.post.views
        
        response = self.client.get(reverse('blog_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Refresh from DB and check views incremented
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, initial_views + 1)
    
    def test_unpublished_post_not_accessible(self):
        """Test that unpublished posts return 404."""
        unpublished = BlogPost.objects.create(
            title="Unpublished Post",
            slug="unpublished-post",
            excerpt="Test",
            content="Test",
            is_published=False
        )
        response = self.client.get(reverse('blog_detail', args=[unpublished.slug]))
        self.assertEqual(response.status_code, 404)

