
import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

import sqlparse

def run_sql_file(filename):
    print(f"Reading {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use sqlparse to safely split statements
    statements = sqlparse.split(content)
    
    print(f"Found {len(statements)} statements.")
    
    count = 0
    with connection.cursor() as cursor:
        for sql in statements:
            sql = sql.strip()
            if not sql:
                continue
            try:
                cursor.execute(sql)
                count += 1
                print(f"Executed block {count} ({count * 100} records)...")
                sys.stdout.flush()
            except Exception as e:
                print(f"Error executing block: {e}")
                
    print("Done!")

if __name__ == '__main__':
    run_sql_file('seed_members.sql')
