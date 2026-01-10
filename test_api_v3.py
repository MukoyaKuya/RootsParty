import requests
import json

API_BASE = "https://kenyaareadata.vercel.app/api/areas"
API_KEY = "keyPub1569gsvndc123kg9sjhg"

print("--- Testing List All ---")
try:
    res = requests.get(f"{API_BASE}?apiKey={API_KEY}")
    if res.status_code == 200:
        data = res.json()
        print("Keys returned:", list(data.keys())[:10]) # Print first 10 to see structure
        # If it returns a list of counties, we can search it
        all_keys = list(data.keys())
        
        search_terms = ["Murang", "Tharaka", "Nairobi", "Elgeyo"]
        for term in search_terms:
            matches = [k for k in all_keys if term.lower() in k.lower()]
            print(f"Matches for '{term}': {matches}")
    else:
        print(f"List all failed: {res.status_code}")
except Exception as e:
    print(f"List all error: {e}")
