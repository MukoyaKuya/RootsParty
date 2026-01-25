"""
Data validation utilities for the Roots Party platform.
Provides validation functions for phone numbers, ID numbers, and other Kenyan data formats.
"""
import re
from django.core.exceptions import ValidationError


def validate_kenyan_phone_number(phone_number):
    """
    Validate Kenyan phone number format.
    
    Accepts formats:
    - 0712345678 (10 digits starting with 0)
    - +254712345678 (international format)
    - 254712345678 (without +)
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        str: Normalized phone number (10 digits starting with 0)
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone_number:
        raise ValidationError("Phone number is required.")
    
    # Remove whitespace and common separators
    phone = re.sub(r'[\s\-\(\)]', '', str(phone_number).strip())
    
    # Check for international format (+254 or 254)
    if phone.startswith('+254'):
        phone = '0' + phone[4:]
    elif phone.startswith('254'):
        phone = '0' + phone[3:]
    
    # Validate format: should be 10 digits starting with 0
    if not re.match(r'^0[17]\d{8}$', phone):
        raise ValidationError(
            "Invalid phone number format. Use format: 0712345678 or +254712345678"
        )
    
    return phone


def validate_kenyan_id_number(id_number):
    """
    Validate Kenyan National ID number format.
    
    Kenyan ID numbers are typically 8 digits, but can be longer for passports.
    This function validates the basic format.
    
    Args:
        id_number (str): ID number to validate
        
    Returns:
        str: Normalized ID number
        
    Raises:
        ValidationError: If ID number is invalid
    """
    if not id_number:
        raise ValidationError("ID number is required.")
    
    # Remove whitespace and convert to string
    id_num = str(id_number).strip().replace(' ', '').replace('-', '')
    
    # Check if it's all digits
    if not id_num.isdigit():
        raise ValidationError("ID number must contain only digits.")
    
    # Kenyan ID numbers are typically 8 digits, but passports can be longer
    # Accept 6-12 digits to be flexible
    if len(id_num) < 6 or len(id_num) > 12:
        raise ValidationError(
            "ID number must be between 6 and 12 digits long."
        )
    
    return id_num


def validate_email(email):
    """
    Enhanced email validation.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        str: Normalized email (lowercase)
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        return None  # Email is optional in many cases
    
    email = email.strip().lower()
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email address format.")
    
    return email


def normalize_phone_number(phone_number):
    """
    Normalize phone number to standard format (0712345678).
    Does not raise errors, returns None if invalid.
    
    Args:
        phone_number (str): Phone number to normalize
        
    Returns:
        str or None: Normalized phone number or None if invalid
    """
    try:
        return validate_kenyan_phone_number(phone_number)
    except ValidationError:
        return None


def is_valid_kenyan_phone(phone_number):
    """
    Check if phone number is valid without raising exceptions.
    
    Args:
        phone_number (str): Phone number to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        validate_kenyan_phone_number(phone_number)
        return True
    except ValidationError:
        return False


def is_valid_kenyan_id(id_number):
    """
    Check if ID number is valid without raising exceptions.
    
    Args:
        id_number (str): ID number to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        validate_kenyan_id_number(id_number)
        return True
    except ValidationError:
        return False
