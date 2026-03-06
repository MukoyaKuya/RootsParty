"""
Tests for core.cache_utils cache helper functions.

Ensures get_cached_county_stats and get_cached_leaders work correctly
with the County and Leader models (correct field names, no FieldError).
"""
from django.test import TestCase, override_settings
from django.core.cache import cache

from core.models import County, Leader
from core.cache_utils import get_cached_county_stats, get_cached_leaders


class GetCachedCountyStatsTest(TestCase):
    """Test get_cached_county_stats returns valid county data with aspirant counts."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_returns_empty_list_when_no_counties(self):
        """Empty database returns empty list."""
        result = get_cached_county_stats(timeout=60)
        self.assertEqual(result, [])

    def test_returns_county_stats_with_expected_fields(self):
        """County stats include id, name, slug, aspirant_count, verified_count."""
        County.objects.create(name="Nairobi", slug="nairobi", code="047")
        County.objects.create(name="Mombasa", slug="mombasa", code="001")

        result = get_cached_county_stats(timeout=60)

        self.assertEqual(len(result), 2)
        for row in result:
            self.assertIn("id", row)
            self.assertIn("name", row)
            self.assertIn("slug", row)
            self.assertIn("aspirant_count", row)
            self.assertIn("verified_count", row)
            self.assertIsInstance(row["aspirant_count"], int)
            self.assertIsInstance(row["verified_count"], int)

    def test_aspirant_counts_reflect_data(self):
        """Aspirant counts are correct when aspirants exist."""
        county = County.objects.create(name="Nairobi", slug="nairobi")
        # Create aspirant registrations linked to county
        from aspirants.models import AspirantRegistration

        AspirantRegistration.objects.create(
            id_number="12345678",
            surname="Test",
            other_names="User",
            phone_number="0700000000",
            position="mca",
            county=county,
            constituency="Westlands",
            ward="Parklands",
            status="submitted",
            is_verified=True,
        )
        AspirantRegistration.objects.create(
            id_number="22345678",
            surname="Test2",
            other_names="User2",
            phone_number="0711111111",
            position="mp",
            county=county,
            constituency="Dagoretti",
            ward="Kawangware",
            status="submitted",
            is_verified=False,
        )

        result = get_cached_county_stats(timeout=60)

        nairobi_row = next(r for r in result if r["slug"] == "nairobi")
        self.assertEqual(nairobi_row["aspirant_count"], 2)
        self.assertEqual(nairobi_row["verified_count"], 1)


class GetCachedLeadersTest(TestCase):
    """Test get_cached_leaders returns valid leader data with role field."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_returns_empty_list_when_no_leaders(self):
        """Empty database returns empty list."""
        result = get_cached_leaders(timeout=60)
        self.assertEqual(result, [])

    def test_returns_leaders_with_role_field(self):
        """Leaders include role (not position) to match Leader model."""
        Leader.objects.create(
            name="George Wajackoyah",
            role="Party Leader",
            slug="george-wajackoyah",
        )
        Leader.objects.create(
            name="Deputy Leader",
            role="Deputy Party Leader",
            slug="deputy-leader",
        )

        result = get_cached_leaders(timeout=60)

        self.assertEqual(len(result), 2)
        for row in result:
            self.assertIn("id", row)
            self.assertIn("name", row)
            self.assertIn("slug", row)
            self.assertIn("role", row)
            self.assertNotIn("position", row)

        roles = {r["role"] for r in result}
        self.assertIn("Party Leader", roles)
        self.assertIn("Deputy Party Leader", roles)
