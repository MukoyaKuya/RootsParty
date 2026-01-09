
import requests
import re
import sys

url = "https://roots-party-1073897174388.europe-north1.run.app/about/"
print(f"Fetching {url}...")

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    # Simple regex for src
    # Look for storage.googleapis.com
    # or just any src
    content = response.text
    
    print("Searching for storage.googleapis.com...")
    matches = re.findall(r'https?://storage\.googleapis\.com/[^"\']+', content)
    
    if matches:
        print("Found GCS URLs:")
        for m in matches[:5]: # Show first 5
            print(m)
            
        # Extract bucket name
        # Format: https://storage.googleapis.com/BUCKET_NAME/path/to/file
        # or https://BUCKET_NAME.storage.googleapis.com/...
        
        first = matches[0]
        if 'storage.googleapis.com/' in first:
            bucket = first.split('storage.googleapis.com/')[1].split('/')[0]
            print(f"\nPOSSIBLE BUCKET NAME: {bucket}")
    else:
        print("No storage.googleapis.com found. Searching for other images...")
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        for img in imgs[:5]:
            print(f"Img: {img}")
            
except Exception as e:
    print(f"Error: {e}")
