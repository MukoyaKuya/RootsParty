import os
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Loads members from a large JSON fixture in chunks to avoid memory issues.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON fixture file')
        parser.add_argument('--chunk-size', type=int, default=1000, help='Number of records per chunk')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        chunk_size = kwargs['chunk_size']

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"File {json_file} does not exist."))
            return

        self.stdout.write(f"Reading {json_file}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data)
        self.stdout.write(f"Total records to load: {total}")
        
        chunks = [data[i:i + chunk_size] for i in range(0, total, chunk_size)]
        
        self.stdout.write(f"Split into {len(chunks)} chunks of {chunk_size} records.")
        
        for i, chunk in enumerate(chunks):
            temp_filename = f'temp_users_chunk_{i}.json'
            with open(temp_filename, 'w', encoding='utf-8') as tf:
                json.dump(chunk, tf)
                
            self.stdout.write(f"Loading chunk {i+1}/{len(chunks)} ({len(chunk)} records)...")
            try:
                call_command('loaddata', temp_filename)
                self.stdout.write(self.style.SUCCESS("  - Success"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Failed: {e}"))
                
            # Clean up
            try:
                os.remove(temp_filename)
            except:
                pass
