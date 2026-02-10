import json
import os
import requests
from pathlib import Path

# Config
BACKUP_FILE = 'cloud_backup.json'
BUCKET_NAME = "roots-party-media-storage"
BASE_URL = f"https://storage.googleapis.com/{BUCKET_NAME}/"
MEDIA_ROOT = Path("media")

# Extensions to look for
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.mp4'}

def download_file(rel_path):
    if not rel_path:
        return

    # Basic cleanup
    rel_path = rel_path.strip()
    
    # Check extension
    _, ext = os.path.splitext(rel_path)
    if ext.lower() not in EXTENSIONS:
        return

    local_path = MEDIA_ROOT / rel_path
    remote_url = f"{BASE_URL}{rel_path}"

    if local_path.exists():
        # Check if it's a placeholder (small size)
        if local_path.stat().st_size < 5120: # 5KB
             print(f"  Overwriting placeholder: {rel_path}")
        else:
             print(f"  Skipping existing: {rel_path}")
             return

    # Ensure dir
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return # Invalid path

    print(f"Downloading: {rel_path}")
    try:
        r = requests.get(remote_url, timeout=10)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
        else:
            print(f"  Failed ({r.status_code})")
    except Exception as e:
        print(f"  Error: {e}")

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
            download_file(data)

# Python 2/3 compat for string chck
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

    print("Scanning for media files...")
    traverse(data)
    print("Done.")

if __name__ == "__main__":
    main()
