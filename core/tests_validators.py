"""
Tests for validation utilities.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.utils.validators import (
    validate_kenyan_phone_number,
    validate_kenyan_id_number,
    validate_email,
    normalize_phone_number,
    is_valid_kenyan_phone,
    is_valid_kenyan_id
)


class PhoneNumberValidationTest(TestCase):
    """Test phone number validation."""
    
    def test_valid_phone_formats(self):
        """Test various valid phone number formats."""
        valid_numbers = [
            "0712345678",
            "+254712345678",
            "254712345678",
            "0712 345 678",
            "0712-345-678",
        ]
        
        for phone in valid_numbers:
            normalized = validate_kenyan_phone_number(phone)
            self.assertEqual(normalized, "0712345678")
    
    def test_invalid_phone_formats(self):
        """Test invalid phone number formats."""
        invalid_numbers = [
            "1234567890",  # Doesn't start with 0
            "071234567",   # Too short
            "07123456789", # Too long
            "abc123",      # Contains letters
            "",            # Empty
        ]
        
        for phone in invalid_numbers:
            with self.assertRaises(ValidationError):
                validate_kenyan_phone_number(phone)
    
    def test_normalize_phone_number(self):
        """Test phone number normalization without exceptions."""
        self.assertEqual(normalize_phone_number("0712345678"), "0712345678")
        self.assertEqual(normalize_phone_number("+254712345678"), "0712345678")
        self.assertIsNone(normalize_phone_number("invalid"))
    
    def test_is_valid_kenyan_phone(self):
        """Test phone validation check without exceptions."""
        self.assertTrue(is_valid_kenyan_phone("0712345678"))
        self.assertTrue(is_valid_kenyan_phone("+254712345678"))
        self.assertFalse(is_valid_kenyan_phone("1234567890"))
        self.assertFalse(is_valid_kenyan_phone(""))


class IDNumberValidationTest(TestCase):
    """Test ID number validation."""
    
    def test_valid_id_numbers(self):
        """Test valid ID number formats."""
        valid_ids = [
            "12345678",
            "123456789012",
            "123456",
        ]
        
        for id_num in valid_ids:
            normalized = validate_kenyan_id_number(id_num)
            self.assertEqual(normalized, id_num)
    
    def test_invalid_id_numbers(self):
        """Test invalid ID number formats."""
        invalid_ids = [
            "12345",      # Too short
            "1234567890123",  # Too long
            "abc123",     # Contains letters
            "",           # Empty
        ]
        
        for id_num in invalid_ids:
            with self.assertRaises(ValidationError):
                validate_kenyan_id_number(id_num)
    
    def test_is_valid_kenyan_id(self):
        """Test ID validation check without exceptions."""
        self.assertTrue(is_valid_kenyan_id("12345678"))
        self.assertFalse(is_valid_kenyan_id("12345"))
        self.assertFalse(is_valid_kenyan_id("abc123"))


class EmailValidationTest(TestCase):
    """Test email validation."""
    
    def test_valid_emails(self):
        """Test valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.com",
        ]
        
        for email in valid_emails:
            normalized = validate_email(email)
            self.assertEqual(normalized, email.lower().strip())
    
    def test_invalid_emails(self):
        """Test invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                validate_email(email)
    
    def test_empty_email(self):
        """Test that empty email returns None."""
        self.assertIsNone(validate_email(""))
        self.assertIsNone(validate_email(None))
