import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Config
BACKUP_FILE = 'cloud_backup.json'
MEDIA_ROOT = Path("media")

# Extensions to look for
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def create_placeholder(rel_path):
    if not rel_path:
        return

    # Basic cleanup
    rel_path = rel_path.strip()
    
    # Check extension
    _, ext = os.path.splitext(rel_path)
    if ext.lower() not in EXTENSIONS:
        return

    local_path = MEDIA_ROOT / rel_path

    if local_path.exists():
        return

    # Ensure dir
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return # Invalid path

    print(f"Creating placeholder: {rel_path}")
    try:
        # Create a simple image
        img = Image.new('RGB', (200, 200), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10,10), "MISSING", fill=(255,255,0))
        
        # Save
        if ext.lower() == '.jpg' or ext.lower() == '.jpeg':
            img.save(local_path, 'JPEG')
        elif ext.lower() == '.png':
            img.save(local_path, 'PNG')
        elif ext.lower() == '.gif':
            img.save(local_path, 'GIF')
        elif ext.lower() == '.webp':
            img.save(local_path, 'WEBP')
            
    except Exception as e:
        print(f"  Error creating placeholder: {e}")

def traverse(data):
    if isinstance(data, dict):
        for key, value in data.items():
            traverse(value)
    elif isinstance(data, list):
        for item in data:
            traverse(item)
    elif isinstance(data, string_types):
        # Potential file path
        if any(data.lower().endswith(ext) for ext in EXTENSIONS):
            create_placeholder(data)

# Python 2/3 compat for string check
try:
    string_types = (str, unicode)
except NameError:
    string_types = (str,)

def main():
    print(f"Reading {BACKUP_FILE}...")
    try:
        with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read json: {e}")
        return

    print("Scanning for missing media files to create placeholders...")
    traverse(data)
    print("Done.")

if __name__ == "__main__":
    main()
