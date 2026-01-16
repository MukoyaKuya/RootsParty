from django.test import TestCase
from .models import Donation

class DonationModelTest(TestCase):
    def test_donation_creation(self):
        donation = Donation.objects.create(
            phone_number="0712345678",
            amount=500.00
        )
        self.assertEqual(donation.status, "PENDING")
        self.assertEqual(str(donation), "0712345678 - 500.0")
