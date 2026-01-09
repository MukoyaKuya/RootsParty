
import os
import sys
import requests
import django
from pathlib import Path

# Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.db import models

# Models to scan
from core.models import Leader, HomeVideo, BlogPost, County, GalleryPost, Product, Resource, PageContent, ContactMessage, LeaderImage, PostImage, Event
from users.models import Member
from finance.models import Donation

BUCKET_NAME = "roots-party-media-storage"
BASE_URL = f"https://storage.googleapis.com/{BUCKET_NAME}/"

# Build list of models and fields
MODELS = [
    Leader, HomeVideo, BlogPost, County, GalleryPost, Product, Resource, PageContent, 
    LeaderImage, PostImage, Event
]

def download_file(field_file):
    if not field_file:
        return

    # Get relative path (e.g. leaders/foo.jpg)
    rel_path = str(field_file)
    if not rel_path or rel_path == 'None':
        return

    # Local path
    local_path = Path(settings.MEDIA_ROOT) / rel_path
    
    # Remote URL
    remote_url = f"{BASE_URL}{rel_path}"

    if local_path.exists():
        # print(f"Skipping {rel_path} (exists)")
        return

    print(f"Downloading {rel_path}...")
    
    # Ensure dir exists
    local_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        r = requests.get(remote_url, timeout=10)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
            print(f"  Success: {local_path}")
        else:
            print(f"  Failed ({r.status_code}): {remote_url}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    print(f"Scanning models for media files in bucket: {BUCKET_NAME}")
    print(f"Target dir: {settings.MEDIA_ROOT}")
    
    # Iterate all models
    count = 0
    for model in MODELS:
        print(f"\nChecking model: {model.__name__}")
        # Find FileField/ImageField
        file_fields = []
        for field in model._meta.fields:
            if isinstance(field, (models.FileField, models.ImageField)):
                file_fields.append(field.name)
        
        if not file_fields:
            continue
            
        # Get all objects
        objects = model.objects.all()
        print(f"  Found {objects.count()} objects. Fields: {file_fields}")
        
        for obj in objects:
            for field_name in file_fields:
                field_file = getattr(obj, field_name)
                download_file(field_file)
                count += 1
                
    print("\nDone!")

if __name__ == "__main__":
    main()
