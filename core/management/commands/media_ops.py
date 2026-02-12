import os
import re
import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models
from django.apps import apps
from core.models import FloatingImage

class Command(BaseCommand):
    help = 'Consolidated media and GCS operations: download, upload, and auditing.'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')
        
        # Subcommand: download
        subparsers.add_parser('download', help='Download media files from GCS to local storage')
        
        # Subcommand: upload
        subparsers.add_parser('upload', help='Upload local media files to GCS bucket')
        
        # Subcommand: download-backup
        subparsers.add_parser('download-backup', help='Scan cloud_backup.json and download missing media')
        
        # Subcommand: placeholders
        subparsers.add_parser('placeholders', help='Scan cloud_backup.json and create placeholders for missing media')
        
        # Subcommand: find-bucket
        subparsers.add_parser('find-bucket', help='Detect active GCS bucket from the live site')
        
        # Subcommand: find-floating
        subparsers.add_parser('find-floating', help='Audit the floating image used on the homepage')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'download':
            self.download_media()
        elif action == 'upload':
            self.upload_media()
        elif action == 'download-backup':
            self.download_from_backup()
        elif action == 'placeholders':
            self.create_placeholders()
        elif action == 'find-bucket':
            self.find_bucket()
        elif action == 'find-floating':
            self.find_floating()
        else:
            self.print_help('manage.py', 'media_ops')

    def download_media(self):
        bucket_name = getattr(settings, 'GS_BUCKET_NAME', 'roots-party-media-storage')
        base_url = f"https://storage.googleapis.com/{bucket_name}/"
        media_root = Path(settings.MEDIA_ROOT)
        
        self.stdout.write(f"Scanning all models for media files in bucket: {bucket_name}")
        self.stdout.write(f"Target dir: {media_root}")
        
        count = 0
        all_models = apps.get_models()
        
        for model in all_models:
            file_fields = [f.name for f in model._meta.fields if isinstance(f, (models.FileField, models.ImageField))]
            if not file_fields:
                continue
                
            self.stdout.write(f"\nChecking model: {model.__name__} (App: {model._meta.app_label})")
            objects = model.objects.all()
            
            for obj in objects:
                for field_name in file_fields:
                    field_file = getattr(obj, field_name)
                    if not field_file or str(field_file) == 'None':
                        continue
                        
                    rel_path = str(field_file)
                    local_path = media_root / rel_path
                    remote_url = f"{base_url}{rel_path}"
                    
                    if local_path.exists():
                        continue
                        
                    self.stdout.write(f"Downloading {rel_path}...")
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        r = requests.get(remote_url, timeout=10)
                        if r.status_code == 200:
                            with open(local_path, 'wb') as f:
                                f.write(r.content)
                            self.stdout.write(self.style.SUCCESS(f"  Success: {rel_path}"))
                            count += 1
                        else:
                            self.stdout.write(self.style.WARNING(f"  Failed ({r.status_code}): {remote_url}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error downloading {rel_path}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nDone! Downloaded {count} files."))

    def upload_media(self):
        try:
            from google.cloud import storage
        except ImportError:
            self.stdout.write(self.style.ERROR("Error: google-cloud-storage not installed."))
            return

        bucket_name = getattr(settings, 'GS_BUCKET_NAME', 'roots-party-media-storage')
        self.stdout.write(f"Initializing upload to GCS bucket: {bucket_name}...")
        
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            media_dir = Path(settings.MEDIA_ROOT)
            
            if not media_dir.exists():
                self.stdout.write(self.style.ERROR(f"Media directory {media_dir} does not exist."))
                return

            uploaded_count = 0
            for file_path in media_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(media_dir)
                    blob_name = str(relative_path).replace("\\", "/")
                    
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(str(file_path))
                    uploaded_count += 1
                    self.stdout.write(f"Uploaded: {blob_name}")

            self.stdout.write(self.style.SUCCESS(f"\nTotal files uploaded: {uploaded_count}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Upload failed: {e}"))

    def download_from_backup(self):
        import json
        backup_file = os.path.join(settings.BASE_DIR, 'cloud_backup.json')
        bucket_name = getattr(settings, 'GS_BUCKET_NAME', 'roots-party-media-storage')
        base_url = f"https://storage.googleapis.com/{bucket_name}/"
        media_root = Path(settings.MEDIA_ROOT)
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.mp4'}

        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f"Backup file {backup_file} not found."))
            return

        self.stdout.write(f"Reading {backup_file} and scanning for media...")
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            paths = self._extract_paths(data, extensions)
            self.stdout.write(f"Found {len(paths)} unique potential media paths.")
            
            count = 0
            for rel_path in paths:
                local_path = media_root / rel_path
                if local_path.exists() and local_path.stat().st_size > 5120:
                    continue
                
                remote_url = f"{base_url}{rel_path}"
                self.stdout.write(f"Downloading: {rel_path}...")
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    r = requests.get(remote_url, timeout=10)
                    if r.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(r.content)
                        count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"  Failed ({r.status_code})"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f"Done! Downloaded {count} files."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Backup process failed: {e}"))

    def create_placeholders(self):
        import json
        backup_file = os.path.join(settings.BASE_DIR, 'cloud_backup.json')
        media_root = Path(settings.MEDIA_ROOT)
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f"Backup file {backup_file} not found."))
            return

        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self.stdout.write(self.style.ERROR("Error: Pillow not installed."))
            return

        self.stdout.write(f"Generating placeholders for missing files in {backup_file}...")
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            paths = self._extract_paths(data, extensions)
            count = 0
            for rel_path in paths:
                local_path = media_root / rel_path
                if local_path.exists():
                    continue
                
                local_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    img = Image.new('RGB', (200, 200), color=(73, 109, 137))
                    d = ImageDraw.Draw(img)
                    d.text((10,10), "MISSING", fill=(255,255,0))
                    
                    ext = os.path.splitext(rel_path)[1].lower()
                    fmt = 'JPEG' if ext in ['.jpg', '.jpeg'] else ext[1:].upper()
                    img.save(local_path, fmt)
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error creating {rel_path}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"Done! Created {count} placeholders."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Placeholder generation failed: {e}"))

    def _extract_paths(self, data, extensions):
        paths = set()
        def _traverse(node):
            if isinstance(node, dict):
                for v in node.values(): _traverse(v)
            elif isinstance(node, list):
                for i in node: _traverse(i)
            elif isinstance(node, str):
                if any(node.lower().endswith(ext) for ext in extensions):
                    paths.add(node.strip())
        _traverse(data)
        return paths

    def find_bucket(self):
        # Default to production URL or settings
        url = getattr(settings, 'SITE_BASE_URL', "https://rootsparty.co.ke") + "/about/"
        self.stdout.write(f"Fetching {url} to identify bucket...")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            matches = re.findall(r'https?://storage\.googleapis\.com/[^"\']+', content)
            if matches:
                self.stdout.write(self.style.SUCCESS("Found GCS URLs in the live site:"))
                for m in matches[:3]:
                    self.stdout.write(f"  - {m}")
                    
                first = matches[0]
                if 'storage.googleapis.com/' in first:
                    bucket = first.split('storage.googleapis.com/')[1].split('/')[0]
                    self.stdout.write(self.style.SUCCESS(f"\nDETECTED BUCKET NAME: {bucket}"))
            else:
                self.stdout.write(self.style.WARNING("No GCS URLs found on the live site."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching site: {e}"))

    def find_floating(self):
        george_image = FloatingImage.objects.filter(name__icontains='george').first()
        
        if george_image and george_image.image:
            self.stdout.write("=" * 60)
            self.stdout.write("FLOATING IMAGE AUDIT")
            self.stdout.write("=" * 60)
            self.stdout.write(f"Name: {george_image.name}")
            self.stdout.write(f"Position: {george_image.get_position_display()}")
            self.stdout.write(f"Active: {george_image.is_active}")
            self.stdout.write(f"\nImage File:")
            self.stdout.write(f"  URL: {george_image.image.url}")
            
            try:
                file_path = george_image.image.path
                self.stdout.write(f"  Full Path: {file_path}")
                self.stdout.write(f"  File Exists: {os.path.exists(file_path)}")
            except Exception:
                self.stdout.write("  Full Path: N/A (Stored in Cloud)")
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Note: If the JuaGig logo is visible, upload a new clean image in Django Admin.")
        else:
            self.stdout.write("No 'GEORGE WAJACKOYAH' floating image found in database.")
