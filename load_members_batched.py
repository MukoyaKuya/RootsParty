
import os
import json
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Member
from django.core.management import call_command

def load_in_chunks(json_file, chunk_size=1000):
    print(f"Reading {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    print(f"Total records to load: {total}")
    
    # We can't easily use bulk_create with raw fixture data because of pk/model handling
    # So we will split the list into smaller lists and save them as temp files, 
    # then run loaddata on each temp file.
    
    chunks = [data[i:i + chunk_size] for i in range(0, total, chunk_size)]
    
    print(f"Split into {len(chunks)} chunks of {chunk_size} records.")
    
    for i, chunk in enumerate(chunks):
        temp_filename = f'temp_users_chunk_{i}.json'
        with open(temp_filename, 'w', encoding='utf-8') as tf:
            json.dump(chunk, tf)
            
        print(f"Loading chunk {i+1}/{len(chunks)} ({len(chunk)} records)...")
        try:
            call_command('loaddata', temp_filename)
            print(f"  - Success")
        except Exception as e:
            print(f"  - Failed: {e}")
            
        # Clean up
        try:
            os.remove(temp_filename)
        except:
            pass

if __name__ == '__main__':
    load_in_chunks('users_data.json', chunk_size=2000)
