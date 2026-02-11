from django.test import TestCase, Client
from django.urls import reverse
from aspirants.models import Aspirant

class AspirantOrderingTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create aspirants in non-priority order
        Aspirant.objects.create(name="MP Candidate", role="mp", is_active=True)
        Aspirant.objects.create(name="President Candidate", role="president", is_active=True)
        Aspirant.objects.create(name="Governor Candidate", role="governor", is_active=True)
        Aspirant.objects.create(name="MCA Candidate", role="mca", is_active=True)

    def test_aspirant_list_ordering(self):
        """Verify that role=all returns aspirants in priority order (President first)"""
        url = reverse('aspirants:aspirant_list') + '?role=all'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        aspirants = list(response.context['aspirants'])
        
        # Priority order: president (1), governor (2), mp (5), mca (6)
        self.assertEqual(aspirants[0].role, 'president', f"First should be president, got {aspirants[0].role}")
        self.assertEqual(aspirants[1].role, 'governor', f"Second should be governor, got {aspirants[1].role}")
        self.assertEqual(aspirants[2].role, 'mp', f"Third should be mp, got {aspirants[2].role}")
        self.assertEqual(aspirants[3].role, 'mca', f"Fourth should be mca, got {aspirants[3].role}")
        
        # Verify names are sorted within the same priority if there were multiple (not tested here but logic added)
