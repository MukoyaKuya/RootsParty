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
    logo_width = models.IntegerField(default=450, help_text="Target width of the logo in pixels. The image will be automatically resized and optimized on upload.")
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

    def save(self, *args, **kwargs):
        # Process image before saving
        if self.image:
            try:
                from PIL import Image
                import io
                from django.core.files.base import ContentFile
                
                img = Image.open(self.image)
                
                # Only resize if larger than target width
                if img.width > self.logo_width:
                    output_width = self.logo_width
                    ratio = output_width / float(img.width)
                    new_height = int(float(img.height) * ratio)
                    img = img.resize((output_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to WebP for maximum performance
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=85, method=6, lossless=False)
                extension = 'webp'
                
                output.seek(0)
                
                # Replace the image with the optimized version
                name = self.image.name.split('.')[0]
                self.image.save(f"{name}_optimized.{extension}", ContentFile(output.read()), save=False)
                
            except Exception as e:
                print(f"Image optimization failed: {e}")

        # Always ensure is_active uniqueness (latest stays active)
        if self.is_active:
            Splash.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)

        super().save(*args, **kwargs)
        
        # Clear specific splash cache and home cache
        from django.core.cache import cache
        cache.delete('active_site_splash')
        from .cache_utils import invalidate_home_cache
        invalidate_home_cache()

    @classmethod
    def get_active(cls):
        """Get the latest active splash screen"""
        return cls.objects.filter(is_active=True).first()
