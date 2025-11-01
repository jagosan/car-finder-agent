
import requests
import json
import os

# The service name resolves to the correct ClusterIP.
OLLAMA_HOST = "http://34.118.227.125:11434"

url = f"{OLLAMA_HOST}/api/generate"
payload = {
    "model": "gemma3",
    "prompt": "Why is the sky blue?",
    "stream": False
}
headers = {"Content-Type": "application/json"}

print(f"--- Attempting to connect to: {url} ---")
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    print(f"Status Code: {response.status_code}")
    print("--- Response Headers: ---")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print("--- Response Body (first 500 chars): ---")
    print(response.text[:500])
except requests.exceptions.RequestException as e:
    print(f"--- An error occurred: {e} ---")
