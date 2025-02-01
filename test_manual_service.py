import requests
import json

url = "http://localhost:8001/manuals"

data = {
    "appliance_name": "Test Appliance",
    "file_path": "/app/manuals/test.pdf"
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")