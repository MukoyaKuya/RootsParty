from PIL import Image
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models_site_settings import SiteSettings
from core.models import FloatingImage

class Command(BaseCommand):
    help = 'Consolidated logo operations: check, resize, and status management.'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')
        
        # Subcommand: check-alpha
        subparsers.add_parser('check-alpha', help='Check transparency status of static logos')
        
        # Subcommand: status
        subparsers.add_parser('status', help='Check current logo status in SiteSettings')
        
        # Subcommand: resize
        resize_parser = subparsers.add_parser('resize', help='Resize static logo to standard 256x256')
        resize_parser.add_argument('--force', action='store_true', help='Force resize even if already small')
        
        # Subcommand: compress
        compress_parser = subparsers.add_parser('compress', help='Optimize image size and quality')
        compress_parser.add_argument('input', type=str, help='Input file path')
        compress_parser.add_argument('--output', type=str, help='Output file path')
        compress_parser.add_argument('--width', type=int, default=1200, help='Max width')
        compress_parser.add_argument('--format', type=str, default='WEBP', choices=['PNG', 'WEBP', 'JPEG'], help='Output format')
        
        # Subcommand: splash-update
        splash_parser = subparsers.add_parser('splash-update', help='Update active splash record with an image')
        splash_parser.add_argument('file', type=str, help='Image file path')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'check-alpha':
            self.check_alpha()
        elif action == 'status':
            self.logo_status()
        elif action == 'resize':
            self.resize_logo(force=options['force'])
        elif action == 'remove-juagig':
            self.remove_juagig()
        elif action == 'compress':
            self.compress_image(
                input_path=options['input'], 
                output_path=options['output'],
                max_width=options['width'],
                fmt=options['format']
            )
        elif action == 'splash-update':
            self.splash_update(options['file'])
        else:
            self.print_help('manage.py', 'logo_ops')

    def check_alpha(self):
        # ... (stays same)
        logos = ['logo-192.png', 'logo-512.png', 'logo.png']
        base_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
        
        self.stdout.write(f"Checking images in {base_dir}...")
        for name in logos:
            path = os.path.join(base_dir, name)
            if not os.path.exists(path):
                self.stdout.write(self.style.WARNING(f"MISSING: {name}"))
                continue
                
            try:
                img = Image.open(path)
                self.stdout.write(f"\nImage: {name}")
                self.stdout.write(f"  Format: {img.format}")
                self.stdout.write(f"  Mode: {img.mode}")
                self.stdout.write(f"  Size: {img.size}")
                
                if img.mode == 'RGBA':
                    extrema = img.getextrema()
                    if extrema[3][0] < 255:
                        self.stdout.write(self.style.SUCCESS("  Status: Has TRANSPARENCY (Alpha channel < 255)"))
                    else:
                        self.stdout.write("  Status: RGBA but verify opaque")
                elif img.mode == 'P':
                     self.stdout.write(f"  Status: Palette mode (transparency info: {img.info.get('transparency')})")
                else:
                    self.stdout.write("  Status: Opaque (No Alpha)")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))

    def logo_status(self):
        # ... (stays same)
        s = SiteSettings.get_settings()
        self.stdout.write("=" * 60)
        self.stdout.write("CURRENT LOGO STATUS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Has logo uploaded: {bool(s.logo)}")
        if s.logo:
            self.stdout.write(f"Logo file name: {s.logo.name}")
            self.stdout.write(f"Logo URL: {s.logo.url}")
            try:
                self.stdout.write(f"Logo path: {s.logo.path}")
            except (AttributeError, NotImplementedError):
                self.stdout.write("Logo path: N/A (Stored in Cloud)")
        else:
            self.stdout.write("No logo uploaded - using default static logo")
            self.stdout.write("Default logo: /static/images/logo.png")
        self.stdout.write("=" * 60)

    def resize_logo(self, force=False):
        # ... (stays same)
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        backup_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_backup.png')

        if not os.path.exists(logo_path):
            self.stdout.write(self.style.ERROR(f"Error: {logo_path} not found."))
            return

        if not os.path.exists(backup_path):
            try:
                img_backup = Image.open(logo_path)
                img_backup.save(backup_path)
                self.stdout.write(self.style.SUCCESS(f"Backup created at {backup_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Backup failed: {e}"))

        with Image.open(logo_path) as img:
            self.stdout.write(f"Original size: {img.size}")
            if img.size[0] > 256 or force:
                new_size = (256, 256)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                img.save(logo_path, optimize=True)
                self.stdout.write(self.style.SUCCESS(f"Resized image saved to {logo_path}. New size: {img.size}"))
            else:
                self.stdout.write("Image is already small enough.")

    def remove_juagig(self):
        # ... (stays same)
        george_images = FloatingImage.objects.filter(
            name__icontains='george'
        ) | FloatingImage.objects.filter(
            name__icontains='wajackoyah'
        )
        
        if george_images.exists():
            count = george_images.count()
            self.stdout.write(f"Found {count} FloatingImage(s) with 'george' or 'wajackoyah':")
            for img in george_images:
                self.stdout.write(f"  - {img.name} (ID: {img.id}, Active: {img.is_active})")
            
            george_images.update(is_active=False)
            self.stdout.write(self.style.SUCCESS("Deactivated GEORGE WAJACKOYAH floating image(s)"))
        else:
            self.stdout.write("No GEORGE WAJACKOYAH floating image found")

    def compress_image(self, input_path, output_path=None, max_width=1200, fmt='WEBP'):
        if not os.path.exists(input_path):
            self.stdout.write(self.style.ERROR(f"File not found: {input_path}"))
            return
            
        if not output_path:
            ext = fmt.lower()
            output_path = f"{os.path.splitext(input_path)[0]}_optimized.{ext}"
            
        try:
            with Image.open(input_path) as img:
                orig_size = os.path.getsize(input_path)
                self.stdout.write(f"Original: {img.format}, {img.size}, {orig_size:,} bytes")
                
                if img.width > max_width:
                    ratio = max_width / float(img.width)
                    new_height = int(float(img.height) * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    self.stdout.write(f"Resized to: {img.size}")
                    
                save_kwargs = {'optimize': True}
                if fmt == 'WEBP':
                    save_kwargs = {'quality': 85, 'method': 6}
                elif fmt == 'JPEG':
                    save_kwargs = {'quality': 85, 'optimize': True}
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                
                img.save(output_path, fmt, **save_kwargs)
                new_size = os.path.getsize(output_path)
                self.stdout.write(self.style.SUCCESS(f"Optimized: {output_path}, {new_size:,} bytes"))
                self.stdout.write(f"Reduction: {(1 - new_size/orig_size)*100:.1f}%")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Compression failed: {e}"))

    def splash_update(self, file_path):
        from core.models_splash import Splash
        from django.core.files import File

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return
            
        splash = Splash.get_active()
        if splash:
            self.stdout.write(f"Updating splash: {splash.title}")
            try:
                with open(file_path, 'rb') as f:
                    splash.image.save(os.path.basename(file_path), File(f), save=True)
                self.stdout.write(self.style.SUCCESS("Splash updated successfully."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Update failed: {e}"))
        else:
            self.stdout.write(self.style.WARNING("No active splash found."))
