from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import County
from .models import AspirantRegistration

User = get_user_model()


class AspirantRegistrationFlowTest(TestCase):
    """Integration tests for aspirant registration (multi-step) flow."""

    def setUp(self):
        self.client = Client()
        self.county = County.objects.create(name="Nairobi", slug="nairobi", code=47)
        self.register_url = reverse('aspirants:aspirant_registration')
        self.status_url = reverse('aspirants:aspirant_status')

    def test_registration_page_loads(self):
        """Registration page returns 200 and shows form."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")  # or a key form label

    def test_registration_submit_success(self):
        """Valid POST creates application and shows success page."""
        data = {
            'id_number': '22345678',
            'surname': 'Ochieng',
            'other_names': 'Jane',
            'phone_number': '0722345678',
            'position': 'mca',
            'county': self.county.id,
            'constituency': 'Westlands',
            'ward': 'Parklands',
            'membership_status': 'new',
            'is_incumbent': 'False',
            'agreed_to_terms': 'on',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aspirants/aspirant_registration_success.html')
        reg = AspirantRegistration.objects.get(id_number='22345678')
        self.assertEqual(reg.status, 'submitted')
        self.assertEqual(reg.surname, 'Ochieng')

    def test_registration_save_draft(self):
        """POST with save_draft creates draft and shows draft_saved page."""
        data = {
            'id_number': '32345678',
            'surname': 'Kamau',
            'other_names': 'Peter',
            'phone_number': '0732345678',
            'save_draft': 'Save draft',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aspirants/aspirant_draft_saved.html')
        reg = AspirantRegistration.objects.get(id_number='32345678')
        self.assertEqual(reg.status, 'draft')

    def test_status_lookup_shows_application(self):
        """Status page POST with id_number returns existing application."""
        AspirantRegistration.objects.create(
            id_number='42345678',
            surname='Mugo',
            other_names='Alice',
            phone_number='0742345678',
            status='submitted',
        )
        response = self.client.post(self.status_url, {'id_number': '42345678'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('aspirant', response.context)
        self.assertEqual(response.context['aspirant'].id_number, '42345678')


class AspirantPDFTest(TestCase):
    """Tests for aspirant PDF views (content-type, filename, staff-only)."""

    def setUp(self):
        self.client = Client()
        self.county = County.objects.create(name="Nairobi", slug="nairobi", code=47)
        self.registration = AspirantRegistration.objects.create(
            id_number='52345678',
            surname='Test',
            other_names='Aspirant',
            phone_number='0752345678',
            position='mp',
            county=self.county,
            status='submitted',
        )
        self.staff = User.objects.create_user(
            username='staffuser', password='testpass123', is_staff=True
        )

    def test_download_aspirant_pdf_anonymous_redirects(self):
        """Anonymous user cannot access aspirant PDF (redirect to login)."""
        url = reverse('aspirants:download_aspirant_pdf', args=[self.registration.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))

    def test_download_aspirant_pdf_staff_returns_processing(self):
        """Staff user gets processing page initially."""
        self.client.login(username='staffuser', password='testpass123')
        url = reverse('aspirants:download_aspirant_pdf', args=[self.registration.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aspirants/profile_processing.html')

    def test_download_aspirants_list_pdf_staff_returns_pdf(self):
        """Staff user gets PDF report directly (sync generation)."""
        self.client.login(username='staffuser', password='testpass123')
        url = reverse('aspirants:download_aspirants_list_pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type', ''), 'application/pdf')
        self.assertIn('attachment', response.get('Content-Disposition', ''))

    def test_download_aspirants_list_pdf_anonymous_redirects(self):
        """Anonymous user cannot access list PDF."""
        url = reverse('aspirants:download_aspirants_list_pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_view_status_redirects(self):
        """Placeholder for status verification."""
        pass
