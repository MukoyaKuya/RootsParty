"""
Comprehensive model tests for core app.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from core.models import (
    Leader, ManifestoItem, ManifestoEvidence, BlogPost, County,
    Event, GatePass, Constituency,
    CarouselImage, HomeVideo, NewsletterSubscriber, ContactMessage
)
from commerce.models import Vendor, Product
from aspirants.models import Aspirant


class LeaderModelTest(TestCase):
    """Test Leader model functionality."""
    
    def test_leader_creation(self):
        """Test creating a leader."""
        leader = Leader.objects.create(
            name="George Wajackoyah",
            role="Party Leader",
            slug="george-wajackoyah"
        )
        self.assertEqual(str(leader), "George Wajackoyah")
        self.assertEqual(leader.slug, "george-wajackoyah")
    
    def test_leader_auto_slug(self):
        """Test automatic slug generation."""
        leader = Leader.objects.create(
            name="Test Leader",
            role="Test Role"
        )
        self.assertEqual(leader.slug, "test-leader")
    
    def test_leader_ordering(self):
        """Test leader ordering by order field."""
        leader1 = Leader.objects.create(name="Leader 1", role="Role", order=2)
        leader2 = Leader.objects.create(name="Leader 2", role="Role", order=1)
        
        leaders = list(Leader.objects.all().order_by('-order'))
        self.assertEqual(leaders[0].name, "Leader 1")  # Higher order first


class ManifestoItemModelTest(TestCase):
    """Test ManifestoItem model."""
    
    def test_manifesto_item_creation(self):
        """Test creating a manifesto item."""
        item = ManifestoItem.objects.create(
            title="Legalize Marijuana",
            slug="legalize-marijuana",
            icon="🌿",
            summary="Legalize cannabis",
            description="Full description"
        )
        self.assertEqual(str(item), "Legalize Marijuana")
    
    def test_manifesto_evidence_auto_slug(self):
        """Test automatic slug generation for evidence."""
        item = ManifestoItem.objects.create(
            title="Test Item",
            slug="test-item",
            icon="🌿",
            summary="Test",
            description="Test"
        )
        evidence = ManifestoEvidence.objects.create(
            item=item,
            country="Canada",
            description="Legalized in 2018"
        )
        self.assertEqual(evidence.slug, "canada")


class BlogPostModelTest(TestCase):
    """Test BlogPost model."""
    
    def test_blog_post_creation(self):
        """Test creating a blog post."""
        post = BlogPost.objects.create(
            title="Test Post",
            excerpt="Test excerpt",
            content="Full content here",
            is_published=True
        )
        self.assertEqual(post.slug, "test-post")
        self.assertEqual(post.views, 0)
    
    def test_blog_post_read_time(self):
        """Test read time calculation."""
        # Create post with ~400 words
        content = "word " * 400
        post = BlogPost.objects.create(
            title="Long Post",
            excerpt="Test",
            content=content,
            is_published=True
        )
        self.assertEqual(post.read_time, "2 min read")
    
    def test_blog_post_youtube_embed_url(self):
        """Test YouTube URL conversion to embed format."""
        post = BlogPost.objects.create(
            title="Video Post",
            excerpt="Test",
            content="Test",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        embed_url = post.get_embed_url()
        self.assertIn("youtube.com/embed", embed_url)
        self.assertIn("dQw4w9WgXcQ", embed_url)


class CountyModelTest(TestCase):
    """Test County model."""
    
    def test_county_creation(self):
        """Test creating a county."""
        county = County.objects.create(
            name="Nairobi",
            code="047",
            presence_status="active"
        )
        self.assertEqual(county.slug, "nairobi")
        self.assertEqual(str(county), "Nairobi")
    
    def test_county_constituency_relationship(self):
        """Test county-constituency relationship."""
        county = County.objects.create(name="Nairobi", slug="nairobi")
        constituency = Constituency.objects.create(
            county=county,
            name="Westlands"
        )
        self.assertEqual(constituency.county, county)
        self.assertEqual(constituency.slug, "westlands")


class EventModelTest(TestCase):
    """Test Event model."""
    
    def test_event_creation(self):
        """Test creating an event."""
        event = Event.objects.create(
            title="Nairobi Rally",
            location="Uhuru Park",
            date=timezone.now() + timedelta(days=7),
            slug="nairobi-rally"
        )
        self.assertTrue(event.is_upcoming)
        self.assertEqual(event.gate_pass_downloads, 0)
    
    def test_event_gate_pass_relationship(self):
        """Test event-gate pass relationship."""
        event = Event.objects.create(
            title="Test Event",
            location="Test",
            date=timezone.now() + timedelta(days=1),
            slug="test-event"
        )
        gate_pass = GatePass.objects.create(
            event=event,
            code="ABC123"
        )
        self.assertEqual(gate_pass.event, event)
        self.assertIn(gate_pass, event.passes.all())


class VendorProductModelTest(TestCase):
    """Test Vendor and Product models."""
    
    def test_vendor_creation(self):
        """Test creating a vendor."""
        vendor = Vendor.objects.create(
            name="Roots Merchandise",
            slug="roots-merchandise"
        )
        self.assertEqual(vendor.slug, "roots-merchandise")
        self.assertTrue(vendor.is_active)
        self.assertFalse(vendor.is_verified)
    
    def test_product_creation(self):
        """Test creating a product."""
        vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor")
        product = Product.objects.create(
            vendor=vendor,
            name="Test Product",
            price=1000.00
        )
        self.assertEqual(product.slug, "test-product")
        self.assertTrue(product.is_available)
        self.assertEqual(product.vendor, vendor)


class AspirantModelTest(TestCase):
    """Test Aspirant model."""
    
    def test_aspirant_creation(self):
        """Test creating an aspirant."""
        county = County.objects.create(name="Nairobi", slug="nairobi")
        constituency = Constituency.objects.create(
            county=county,
            name="Westlands"
        )
        
        aspirant = Aspirant.objects.create(
            name="John Doe",
            role="mp",
            constituency=constituency
        )
        self.assertEqual(aspirant.role, "mp")
        self.assertEqual(aspirant.constituency, constituency)
        self.assertTrue(aspirant.is_active)
    
    def test_aspirant_youtube_embed(self):
        """Test YouTube embed URL generation."""
        aspirant = Aspirant.objects.create(
            name="Test Aspirant",
            role="mp",
            video_url="https://youtu.be/dQw4w9WgXcQ"
        )
        embed_url = aspirant.get_embed_url()
        self.assertIn("youtube.com/embed", embed_url)


class CarouselImageModelTest(TestCase):
    """Test CarouselImage model."""
    
    def test_carousel_image_ordering(self):
        """Test carousel image ordering."""
        img1 = CarouselImage.objects.create(title="Image 1", order=2)
        img2 = CarouselImage.objects.create(title="Image 2", order=1)
        
        images = list(CarouselImage.objects.filter(is_active=True).order_by('order'))
        if images:
            self.assertEqual(images[0].order, 1)


class HomeVideoModelTest(TestCase):
    """Test HomeVideo model."""
    
    def test_home_video_creation(self):
        """Test creating a home video."""
        video = HomeVideo.objects.create(
            title="Watch Our Message",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            is_active=True
        )
        embed_url = video.get_embed_url()
        self.assertIn("youtube", embed_url.lower())


class NewsletterSubscriberModelTest(TestCase):
    """Test NewsletterSubscriber model."""
    
    def test_subscriber_creation(self):
        """Test creating a subscriber."""
        subscriber = NewsletterSubscriber.objects.create(
            email="test@example.com"
        )
        self.assertTrue(subscriber.is_active)
        self.assertEqual(str(subscriber), "test@example.com")
    
    def test_subscriber_unique_email(self):
        """Test that email must be unique."""
        NewsletterSubscriber.objects.create(email="test@example.com")
        
        with self.assertRaises(Exception):  # IntegrityError
            NewsletterSubscriber.objects.create(email="test@example.com")


class ContactMessageModelTest(TestCase):
    """Test ContactMessage model."""
    
    def test_contact_message_creation(self):
        """Test creating a contact message."""
        message = ContactMessage.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="membership",
            message="I want to join"
        )
        self.assertFalse(message.is_read)
        self.assertEqual(message.get_subject_display(), "Membership Inquiry")
