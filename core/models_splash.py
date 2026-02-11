"""
Splash screen management model for Roots Party platform.
Allows admins to manage the splash screen image directly.
"""
from django.db import models

class Splash(models.Model):
    """
    Model for managing the splash screen image.
    Only the latest active splash screen will be displayed.
    """
    ANIMATION_CHOICES = [
        ('palpating', 'Palpating (Pulse)'),
        ('spinning', 'Spinning'),
        ('reveal', 'Logo Reveal (Fade & Scale)'),
        ('floating', 'Floating'),
    ]

    title = models.CharField(max_length=100, default="Main Splash Screen", help_text="Internal name for this splash screen")
    image = models.ImageField(upload_to='site/splash/', help_text="Upload the splash screen image")
    animation = models.CharField(
        max_length=20, 
        choices=ANIMATION_CHOICES, 
        default='reveal',
        help_text="Select the animation for the logo"
    )
    is_active = models.BooleanField(default=True, help_text="Only one active splash screen will be shown")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Splash Screen'
        verbose_name_plural = 'Splash Screens'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"

    @classmethod
    def get_active(cls):
        """Get the latest active splash screen"""
        return cls.objects.filter(is_active=True).first()
