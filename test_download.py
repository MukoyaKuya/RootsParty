import requests

url = "https://storage.googleapis.com/roots-party-media-storage/blog/lumina-enhanced-1768494163546.png"
print(f"Testing download from: {url}")

try:
    r = requests.get(url, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Content Type: {r.headers.get('content-type')}")
    print(f"Content Length: {r.headers.get('content-length')}")
    if r.status_code == 200:
        print("Download successful!")
    else:
        print("Download failed.")
except Exception as e:
    print(f"Error: {e}")
