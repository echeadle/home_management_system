import requests
import json

url = "http://localhost:8001/manuals"
query_url = "http://localhost:8001/query/Refrigerator"

data = {
    "appliance_name": "Refrigerator",
    "file_path": "/app/manuals/test.pdf"
}

query_data = {
    "query":"What is the maintence schedule"
}

try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    
try:
    response = requests.post(query_url, json=query_data)
    response.raise_for_status()
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")