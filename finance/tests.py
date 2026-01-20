from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Donation


class DonationModelTest(TestCase):
    """Test cases for the Donation model."""
    
    def test_donation_creation(self):
        """Test basic donation creation with default status."""
        donation = Donation.objects.create(
            phone_number="0712345678",
            amount=500.00
        )
        self.assertEqual(donation.status, "PENDING")
        self.assertEqual(str(donation), "0712345678 - 500.0")
    
    def test_donation_status_choices(self):
        """Test that all status choices work correctly."""
        for status, _ in [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]:
            donation = Donation.objects.create(
                phone_number="0712345678",
                amount=100.00,
                status=status
            )
            self.assertEqual(donation.status, status)
    
    def test_donation_with_transaction_reference(self):
        """Test donation with unique transaction reference."""
        donation = Donation.objects.create(
            phone_number="0712345678",
            amount=1000.00,
            transaction_reference="MPESA123ABC"
        )
        self.assertEqual(donation.transaction_reference, "MPESA123ABC")


class DonationViewTest(TestCase):
    """Test cases for finance views."""
    
    def setUp(self):
        self.client = Client()
        self.donate_url = reverse('donate')
    
    def test_donate_page_loads(self):
        """Test that the donate page loads correctly."""
        response = self.client.get(self.donate_url)
        self.assertEqual(response.status_code, 200)
    
    def test_donate_post_creates_donation(self):
        """Test that POST to donate endpoint creates a donation record."""
        initial_count = Donation.objects.count()
        response = self.client.post(self.donate_url, {
            'phone': '0712345678',
            'amount': '500'
        })
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        # Should create a donation record
        self.assertEqual(Donation.objects.count(), initial_count + 1)
    
    def test_donate_post_with_custom_amount(self):
        """Test donation with custom amount field."""
        response = self.client.post(self.donate_url, {
            'phone': '0712345678',
            'custom_amount': '2500'
        })
        self.assertEqual(response.status_code, 200)
        donation = Donation.objects.last()
        self.assertEqual(donation.amount, Decimal('2500'))

