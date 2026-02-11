"""
Site-wide settings model for Roots Party platform.
Allows admins to manage logo, branding, and other site-wide settings.
"""
from django.db import models
from django.core.validators import MinValueValidator
from image_cropping import ImageRatioField


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings.
    Only one instance should exist.
    """
    # Logo Settings
    logo = models.ImageField(
        upload_to='site/logo/',
        blank=True,
        null=True,
        help_text="Main party logo displayed on homepage and throughout the site"
    )
    logo_cropping = ImageRatioField(
        'logo',
        '400x400',
        help_text="Crop the logo for optimal display (square format recommended)"
    )
    
    # Alternative logo formats
    logo_square = models.ImageField(
        upload_to='site/logo/',
        blank=True,
        null=True,
        help_text="Square version of logo (for favicons, social media, etc.)"
    )
    
    # Site Information
    site_name = models.CharField(
        max_length=200,
        default="Roots Party",
        help_text="Official site name"
    )
    site_tagline = models.CharField(
        max_length=300,
        default="TINGIZA MTI!",
        blank=True,
        help_text="Site tagline/slogan"
    )
    
    # Contact Information (can be overridden by PageContent)
    contact_email = models.EmailField(
        blank=True,
        help_text="Primary contact email"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Primary contact phone"
    )
    
    # Social Media
    twitter_handle = models.CharField(
        max_length=100,
        blank=True,
        help_text="Twitter handle (without @)"
    )
    facebook_url = models.URLField(
        blank=True,
        help_text="Facebook page URL"
    )
    youtube_url = models.URLField(
        blank=True,
        help_text="YouTube channel URL"
    )
    
    # Carousel Settings
    carousel_duration = models.IntegerField(
        default=8000,
        validators=[MinValueValidator(2000)],
        help_text="Carousel image duration in milliseconds (default: 8000 = 8 seconds). Minimum: 2000ms (2 seconds)"
    )
    
    # Meta Information
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear site settings cache
        from django.core.cache import cache
        cache.delete('site_settings_singleton')
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    @property
    def logo_url(self):
        """Get logo URL, fallback to static if not set"""
        if self.logo:
            return self.logo.url
        return '/static/images/logo.png'
    
    @property
    def logo_square_url(self):
        """Get square logo URL, fallback to static if not set"""
        if self.logo_square:
            return self.logo_square.url
        return '/static/images/logo-192.png'
    
    # Keep methods for backward compatibility
    def get_logo_url(self):
        """Get logo URL, fallback to static if not set"""
        return self.logo_url
    
    def get_logo_square_url(self):
        """Get square logo URL, fallback to static if not set"""
        return self.logo_square_url
