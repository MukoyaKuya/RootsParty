#!/usr/bin/env python
"""
Upload local media files to GCS bucket
"""
import os
from google.cloud import storage
from pathlib import Path

# Initialize GCS client
client = storage.Client(project="gen-lang-client-0549116861")
bucket = client.bucket("roots-party-media-storage")

# Media directory
media_dir = Path("media")

# Upload all files
uploaded_count = 0
for file_path in media_dir.rglob("*"):
    if file_path.is_file():
        # Get relative path from media directory
        relative_path = file_path.relative_to(media_dir)
        blob_name = str(relative_path).replace("\\", "/")
        
        # Upload to GCS
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(file_path))
        uploaded_count += 1
        print(f"Uploaded: {blob_name}")

print(f"\nTotal files uploaded: {uploaded_count}")
print("Media files sync complete!")
