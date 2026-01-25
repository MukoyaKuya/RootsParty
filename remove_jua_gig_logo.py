"""
Script to remove Jua Gig logo from the homepage.
Deactivates the GEORGE WAJACKOYAH floating image if it contains the jua gig logo.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FloatingImage

def remove_jua_gig_logo():
    """Deactivate the GEORGE WAJACKOYAH floating image to remove jua gig logo"""
    
    # Find and deactivate the GEORGE WAJACKOYAH floating image
    george_image = FloatingImage.objects.filter(
        name__icontains='george'
    ) | FloatingImage.objects.filter(
        name__icontains='wajackoyah'
    )
    
    if george_image.exists():
        print(f"Found {george_image.count()} FloatingImage(s) with 'george' or 'wajackoyah':")
        for img in george_image:
            print(f"  - {img.name} (ID: {img.id}, Active: {img.is_active})")
        
        # Deactivate it
        george_image.update(is_active=False)
        print("Deactivated GEORGE WAJACKOYAH floating image")
        print("The homepage will now show the placeholder instead.")
    else:
        print("No GEORGE WAJACKOYAH floating image found")
    
    # List remaining active floating images
    print("\n--- Remaining Active Floating Images ---")
    active_floating = FloatingImage.objects.filter(is_active=True)
    if active_floating.exists():
        for img in active_floating:
            print(f"  - {img.name} (Position: {img.get_position_display()})")
    else:
        print("  No active floating images")

if __name__ == '__main__':
    remove_jua_gig_logo()
