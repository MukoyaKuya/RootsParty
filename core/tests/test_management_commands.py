import os
import io
from unittest import mock
from pathlib import Path
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command
from django.core.files.base import ContentFile
from core import models_site_settings
from core.models import FloatingImage, CarouselImage, ManifestoItem
from commerce.models import Vendor, Product
from django.contrib.auth import get_user_model

User = get_user_model()

class ManagementCommandTests(TestCase):
    def setUp(self):
        # Create common test data
        self.out = io.StringIO()
        self.err = io.StringIO()

    def test_logo_ops_status(self):
        """Test logo_ops status subcommand."""
        # Case 1: No logo
        call_command('logo_ops', 'status', stdout=self.out)
        output = self.out.getvalue()
        self.assertIn("Has logo uploaded: False", output)
        self.assertIn("using default static logo", output)

        # Case 2: With logo
        from PIL import Image
        file_obj = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(255, 0, 0, 0))
        image.save(file_obj, 'png')
        file_obj.seek(0)
        
        settings = models_site_settings.SiteSettings.get_settings()
        settings.logo.save('test_logo.png', ContentFile(file_obj.read()))
        self.out = io.StringIO() # Reset buffer
        call_command('logo_ops', 'status', stdout=self.out)
        output = self.out.getvalue()
        self.assertIn("Has logo uploaded: True", output)

    @mock.patch('PIL.Image.open')
    def test_logo_ops_check_alpha(self, mock_open):
        """Test logo_ops check-alpha."""
        mock_img = mock.MagicMock()
        mock_img.format = 'PNG'
        mock_img.mode = 'RGBA'
        mock_img.size = (100, 100)
        mock_img.getextrema.return_value = [(0, 100), (0, 100), (0, 100), (0, 200)] # Transparent
        mock_open.return_value = mock_img
        
        # Mock os.path.exists to simulate files existing
        with mock.patch('os.path.exists', return_value=True):
            call_command('logo_ops', 'check-alpha', stdout=self.out)
            output = self.out.getvalue()
            self.assertIn("Has TRANSPARENCY", output)

    @mock.patch('requests.get')
    def test_media_ops_find_bucket(self, mock_get):
        """Test media_ops find-bucket."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<img src="https://storage.googleapis.com/test-bucket/foo.jpg">'
        mock_get.return_value = mock_response

        call_command('media_ops', 'find-bucket', stdout=self.out)
        output = self.out.getvalue()
        self.assertIn("DETECTED BUCKET NAME: test-bucket", output)

    def test_media_ops_find_floating(self):
        """Test media_ops find-floating."""
        # Case 1: No image
        call_command('media_ops', 'find-floating', stdout=self.out)
        self.assertIn("No 'GEORGE WAJACKOYAH' floating image found", self.out.getvalue())

        # Case 2: With image
        f = FloatingImage.objects.create(name="George Wajackoyah", is_active=True)
        from PIL import Image
        file_obj = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(255, 0, 0, 0))
        image.save(file_obj, 'png')
        data = file_obj.getvalue()
        f.image.save('george.png', ContentFile(data))
        self.out = io.StringIO()
        call_command('media_ops', 'find-floating', stdout=self.out)
        self.assertIn("FLOATING IMAGE AUDIT", self.out.getvalue())

    def test_db_ops_stats(self):
        """Test db_ops stats."""
        User.objects.create_user(username='testuser', password='password')
        call_command('db_ops', 'stats', stdout=self.out)
        output = self.out.getvalue()
        self.assertIn("DATABASE STATISTICS & AUDIT", output)
        self.assertIn("Total Users: 1", output)

    def test_db_ops_migrate_vendors(self):
        """Test db_ops migrate-vendors."""
        p = Product.objects.create(name="Orphan Product", price=100)
        self.assertIsNone(p.vendor)
        
        call_command('db_ops', 'migrate-vendors', stdout=self.out)
        p.refresh_from_db()
        self.assertIsNotNone(p.vendor)
        self.assertEqual(p.vendor.name, "Roots Official")
        self.assertIn("Migrated 1 products", self.out.getvalue())

    def test_carousel_ops_seed(self):
        """Test carousel_ops seed."""
        # Create dummy images so image_cropping doesn't explode during save
        from PIL import Image
        media_root = Path(settings.MEDIA_ROOT)
        for i in range(1, 4):
            path = media_root / 'carousel' / f'carousel-{i}.jpg'
            path.parent.mkdir(parents=True, exist_ok=True)
            img = Image.new('RGB', (1200, 400), color=(73, 109, 137))
            img.save(path, 'JPEG')

        self.assertEqual(CarouselImage.objects.count(), 0)
        call_command('carousel_ops', 'seed', stdout=self.out)
        self.assertEqual(CarouselImage.objects.count(), 3)
        self.assertIn("Summary: Created 3", self.out.getvalue())

    @mock.patch('PIL.Image.new')
    @mock.patch('PIL.Image.open')
    def test_pwa_ops_fix_icons(self, mock_open, mock_new):
        """Test pwa_ops fix-icons."""
        mock_img = mock.MagicMock()
        mock_img.mode = 'RGBA'
        mock_open.return_value = mock_img
        
        with mock.patch('os.path.exists', return_value=True):
            call_command('pwa_ops', 'fix-icons', stdout=self.out)
            self.assertIn("PWA icons updated", self.out.getvalue())

    def test_db_ops_seed_manifesto(self):
        """Test db_ops seed-manifesto."""
        self.assertEqual(ManifestoItem.objects.count(), 0)
        call_command('db_ops', 'seed-manifesto', stdout=self.out)
        self.assertGreater(ManifestoItem.objects.count(), 0)
        self.assertIn("Manifesto data populated successfully", self.out.getvalue())
