import os
import django
import sys
import re

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import BlogPost

print("Fixing BlogPost cropping values...")
posts = BlogPost.objects.all()

count = 0
for post in posts:
    # Get raw value from DB for checking
    # Accessing post.cropping might trigger descriptor, so safe to use values() or just try/except
    # But since we want to SAVE, we need the object.
    
    # We can use .files or raw SQL, but let's try to just set it to '' if it looks wrong.
    # The descriptor for ImageRatioField might crash on access if it's invalid.
    
    # Strategy: update using queryset.update() to bypass descriptor read
    # But we want to only update invalid ones.
    
    # Let's inspect using .values() first to identify IDs
    raw_val = BlogPost.objects.filter(id=post.id).values('cropping')[0]['cropping']
    
    # Check if valid format: "x,y,w,h" (ints)
    if not raw_val:
        continue
        
    is_valid = re.match(r'^\d+,\d+,\d+,\d+$', raw_val)
    if not is_valid:
        print(f"Invalid cropping value for ID {post.id}: '{raw_val}' -> Clearing.")
        # Update directly in DB
        BlogPost.objects.filter(id=post.id).update(cropping='')
        count += 1

print(f"Fixed {count} posts.")
