import requests
import json

API_BASE = "https://kenyaareadata.vercel.app/api/areas"
API_KEY = "keyPub1569gsvndc123kg9sjhg"

counties_to_test = [
    "Homa Bay",
    "Elgeyo-Marakwet",
    "Murang'a",
    "Nairobi",
    "Tharaka-Nithi",
    "Trans Nzoia"
]

for county in counties_to_test:
    print(f"\n--- Testing: {county} ---")
    try:
        url = f"{API_BASE}?apiKey={API_KEY}&county={county}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            # print(json.dumps(data, indent=2)) 
            # We want to know the keys
            print("Top level keys:", list(data.keys()))
            if county in data:
                print(f"✅ Success! Found key '{county}' with {len(data[county])} constituencies.")
            else:
                print(f"❌ Failed! Key '{county}' not found in response.")
        else:
            print(f"Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Request failed: {e}")
