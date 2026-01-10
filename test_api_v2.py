import requests
import json

API_BASE = "https://kenyaareadata.vercel.app/api/areas"
API_KEY = "keyPub1569gsvndc123kg9sjhg"

variations_to_test = [
    "Nairobi City",
    "Elgeyo Marakwet",
    "Elgeyo/Marakwet",
    "Muranga",
    "Tharaka Nithi"
]

for county in variations_to_test:
    print(f"\n--- Testing: {county} ---")
    try:
        url = f"{API_BASE}?apiKey={API_KEY}&county={county}"
        res = requests.get(url)
        if res.status_code == 200:
            print("✅ Success!")
        else:
            print(f"❌ Failed ({res.status_code})")
    except Exception as e:
        print(f"Request failed: {e}")
