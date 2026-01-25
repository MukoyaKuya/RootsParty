"""
Find the image file being used for the floating image on homepage
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FloatingImage
from django.conf import settings

def find_floating_image():
    """Find the floating image file path"""
    
    # Find the GEORGE WAJACKOYAH floating image
    george_image = FloatingImage.objects.filter(
        name__icontains='george'
    ).first()
    
    if george_image and george_image.image:
        print("=" * 60)
        print("FLOATING IMAGE INFORMATION")
        print("=" * 60)
        print(f"Name: {george_image.name}")
        print(f"Position: {george_image.get_position_display()}")
        print(f"Active: {george_image.is_active}")
        print(f"\nImage File:")
        print(f"  URL: {george_image.image.url}")
        
        try:
            file_path = george_image.image.path
            print(f"  Full Path: {file_path}")
            print(f"  File Exists: {os.path.exists(file_path)}")
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  File Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        except Exception as e:
            print(f"  Could not get file path: {e}")
            print(f"  (This might be using cloud storage)")
        
        print("\n" + "=" * 60)
        print("SOLUTION:")
        print("=" * 60)
        print("The JuaGig logo is embedded IN the image file itself.")
        print("To fix this, you need to:")
        print("  1. Go to Django Admin: /admin/core/floatingimage/")
        print("  2. Edit the 'GEORGE WAJACKOYAH' floating image")
        print("  3. Upload a NEW image file WITHOUT the JuaGig logo")
        print("  4. Save the changes")
        print("\nOR")
        print("  1. Replace the image file directly in the media folder")
        print(f"  2. Location: {file_path if 'file_path' in locals() and os.path.exists(file_path) else 'media/floating/'}")
        print("  3. Keep the same filename")
    else:
        print("No GEORGE WAJACKOYAH floating image found in database")
        print("\nAll FloatingImages:")
        all_images = FloatingImage.objects.all()
        for img in all_images:
            print(f"  - {img.name} (Active: {img.is_active})")

if __name__ == '__main__':
    find_floating_image()
