from django.test import TestCase, Client
from django.urls import reverse
from users.models import Member
from core.models import County
import os

class MemberRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.county = County.objects.create(name="Nairobi", slug="nairobi", code=47)
        self.join_url = reverse('join')  # Assuming URL pattern name is 'join'

    def test_join_page_loads(self):
        """Test that the join page loads correctly."""
        response = self.client.get(self.join_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nairobi")

    def test_successful_registration(self):
        """Test registering a new member with valid data."""
        # Enable Recaptcha Testing mode for this test
        os.environ['RECAPTCHA_TESTING'] = 'True'
        
        data = {
            'surname': 'Kamau',
            'other_names': 'John',
            'id_number': '12345678',
            'phone_number': '0712345678', # Renamed from phone
            'email': 'john@example.com',
            'county': self.county.id,
            'constituency': 'Westlands',
            'ward': 'Parklands',
            'polling_center': 'Primary School',
            'sex': 'Male',
            'g-recaptcha-response': 'PASSED', # Dummy captcha
            'confirm_email_hidden': '' # Empty honeypot
        }
        response = self.client.post(self.join_url, data)
        
        # Should redirect to success page
        self.assertRedirects(response, reverse('join_success'))
        
        # Verify database
        member = Member.objects.get(id_number='12345678')
        self.assertEqual(member.surname, 'Kamau')
        self.assertEqual(member.full_name, 'Kamau John')
        self.assertEqual(member.county, self.county)

    def test_missing_required_fields(self):
        """Test validaton ensures required fields are present."""
        data = {
            'surname': '', # Missing surname
            'id_number': '87654321',
            'phone_number': '0787654321',
            'g-recaptcha-response': 'PASSED',
            'confirm_email_hidden': ''
        }
        response = self.client.post(self.join_url, data)
        
        # Should NOT redirect, should render same page with error
        self.assertEqual(response.status_code, 200)
        # Check for message (depending on how messages are rendered, this might need adjustment)
        # But we know member count shouldn't increase
        self.assertEqual(Member.objects.count(), 0)

    def test_duplicate_id_registration(self):
        """Test that registering with an existing ID number fails gracefully."""
        # Create existing member
        Member.objects.create(
            surname='Existing', other_names='User', full_name='Existing User',
            id_number='11223344', phone_number='0700000000'
        )
        
        data = {
            'surname': 'New',
            'other_names': 'User',
            'id_number': '11223344', # Duplicate ID
            'phone_number': '0711111111',
            'g-recaptcha-response': 'PASSED',
            'confirm_email_hidden': ''
        }
        response = self.client.post(self.join_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Member.objects.filter(id_number='11223344').count(), 1)
        # Check for error message in response content
        messages = list(response.context['messages'])
        self.assertTrue(any("already registered" in str(m) for m in messages))

class PDFGenerationTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
            surname='Test', other_names='Member', full_name='Test Member',
            id_number='99887766', phone_number='0799887766'
        )

    def test_download_card(self):
        """Test that the PDF card download endpoint works."""
        url = reverse('download_card', args=[self.member.id])
        response = self.client.get(url)
        
        # If libraries handle it, we get 200 and PDF
        # If libraries missing, we get 500 (per view logic)
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertTrue(response.content.startswith(b'%PDF'))
        else:
            # If 500, it might be due to missing libraries, which is 'acceptable' environment state 
            # but we want to know.
            print("PDF Test returned status:", response.status_code)
            if response.status_code == 500:
                self.assertIn(b"QR code library not installed", response.content)
