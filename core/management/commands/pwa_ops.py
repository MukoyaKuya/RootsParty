import os
import re
import struct
from PIL import Image
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Consolidated PWA and i18n operations: icon fixing and translation management.'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')
        
        # Subcommand: fix-icons
        subparsers.add_parser('fix-icons', help='Regenerate PWA icons from logo.png with white background')
        
        # Subcommand: update-po
        subparsers.add_parser('update-po', help='Extract translatable strings from templates and update sw PO file')
        
        # Subcommand: compile-mo
        subparsers.add_parser('compile-mo', help='Compile django.po to django.mo for swahili')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'fix-icons':
            self.fix_icons()
        elif action == 'update-po':
            self.update_po()
        elif action == 'compile-mo':
            self.compile_mo()
        else:
            self.print_help('manage.py', 'pwa_ops')

    def fix_icons(self):
        base_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
        source_path = os.path.join(base_dir, 'logo.png')
        target_sizes = [192, 512]

        if not os.path.exists(source_path):
            self.stdout.write(self.style.ERROR(f"Error: Source {source_path} not found!"))
            return

        self.stdout.write(f"Loading source: {source_path}")
        source_img = Image.open(source_path)

        if source_img.mode != 'RGBA':
            self.stdout.write("Warning: Source is not RGBA, converting...")
            source_img = source_img.convert('RGBA')

        for size in target_sizes:
            filename = f"logo-{size}.png"
            target_path = os.path.join(base_dir, filename)
            self.stdout.write(f"\nProcessing {filename}...")
            
            img_copy = source_img.copy()
            img_copy.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            new_img = Image.new("RGB", (size, size), (255, 255, 255))
            pos_x = (size - img_copy.width) // 2
            pos_y = (size - img_copy.height) // 2
            
            new_img.paste(img_copy, (pos_x, pos_y), mask=img_copy)
            new_img.save(target_path, "PNG")
            self.stdout.write(self.style.SUCCESS(f"Saved {target_path} (Size: {size}x{size})"))

        self.stdout.write(self.style.SUCCESS("\nDone! PWA icons updated."))

    def update_po(self):
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        po_file_path = os.path.join(settings.BASE_DIR, 'locale', 'sw', 'LC_MESSAGES', 'django.po')
        
        self.stdout.write("Extracting strings from templates...")
        trans_strings = set()
        trans_pattern = re.compile(r'{%\s*trans\s+"(.*?)"\s*%}')
        
        for root, _, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            matches = trans_pattern.findall(content)
                            for match in matches:
                                trans_strings.add(match)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error reading {file_path}: {e}"))
        
        self.stdout.write(f"Found {len(trans_strings)} unique translatable strings.")

        if not os.path.exists(po_file_path):
            self.stdout.write(self.style.WARNING(f"PO file not found: {po_file_path}. Skipping update."))
            return

        try:
            with open(po_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading PO file: {e}"))
            return

        existing_msgids = set(re.findall(r'msgid "(.*?)"', content))
        
        new_count = 0
        with open(po_file_path, 'a', encoding='utf-8') as f:
            for s in trans_strings:
                if s not in existing_msgids:
                    self.stdout.write(f"Adding new string: {s}")
                    f.write(f'\nmsgid "{s}"\n')
                    f.write('msgstr ""\n')
                    new_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Done. Added {new_count} new strings to {po_file_path}"))

    def compile_mo(self):
        po_file = os.path.join(settings.BASE_DIR, "locale", "sw", "LC_MESSAGES", "django.po")
        mo_file = os.path.join(settings.BASE_DIR, "locale", "sw", "LC_MESSAGES", "django.mo")
        
        if not os.path.exists(po_file):
            self.stdout.write(self.style.ERROR(f"PO file not found: {po_file}"))
            return

        self.stdout.write(f"Compiling {po_file}...")
        
        messages = {}
        current_msgid = None
        current_msgstr = None
        
        with open(po_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('msgid '):
                if current_msgid is not None and current_msgstr is not None:
                    messages[current_msgid] = current_msgstr
                current_msgid = line[6:].strip('"')
                current_msgstr = ""
            elif line.startswith('msgstr '):
                current_msgstr = line[7:].strip('"')
            elif line.startswith('"'):
                if current_msgstr is not None:
                    current_msgstr += line.strip('"')
                elif current_msgid is not None:
                    current_msgid += line.strip('"')

        if current_msgid is not None and current_msgstr is not None:
            messages[current_msgid] = current_msgstr

        keys = sorted(messages.keys())
        count = len(keys)
        
        string_buffer = bytearray()
        key_descriptors = []
        val_descriptors = []
        datastart = 28 + (2 * count * 8)
        
        for k in keys:
            v = messages[k]
            k_bytes = k.encode('utf-8') + b'\0'
            k_len = len(k_bytes) - 1
            k_off = datastart + len(string_buffer)
            string_buffer.extend(k_bytes)
            key_descriptors.append((k_len, k_off))
            
            v_bytes = v.encode('utf-8') + b'\0'
            v_len = len(v_bytes) - 1
            v_off = datastart + len(string_buffer)
            string_buffer.extend(v_bytes)
            val_descriptors.append((v_len, v_off))
            
        try:
            with open(mo_file, 'wb') as f:
                f.write(struct.pack('<I', 0x950412de)) # Magic
                f.write(struct.pack('<I', 0))          # Version
                f.write(struct.pack('<I', count))      # N
                f.write(struct.pack('<I', 28))         # Offset originals
                f.write(struct.pack('<I', 28 + count * 8)) # Offset translations
                f.write(struct.pack('<I', 0))          # Hash size
                f.write(struct.pack('<I', 0))          # Hash offset
                
                for l, o in key_descriptors:
                    f.write(struct.pack('<II', l, o))
                for l, o in val_descriptors:
                    f.write(struct.pack('<II', l, o))
                f.write(string_buffer)
                
            self.stdout.write(self.style.SUCCESS(f"Compiled {count} messages to {mo_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Compilation failed: {e}"))
