import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import BlogPost

print("Inspecting BlogPost raw values...")
# values() returns a dict, bypassing model field descriptors
posts = BlogPost.objects.all().values('id', 'title', 'image', 'cropping')

for post in posts:
    print(f"ID: {post['id']}, Title: {post['title']}")
    print(f"  Cropping (Raw): '{post.get('cropping', 'FIELD NOT FOUND')}'")
    print(f"  Image: '{post.get('image')}'")
    print("-" * 30)
