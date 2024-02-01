import json
import requests

# Load data from JSON file
json_file_path = 'tnydb.json'  # Replace with the actual path to your JSON file

with open(json_file_path, 'r') as file:
    json_data = json.load(file)

default_data = json_data.get("_default", {})
bad_values = [entry["data"]["bad"] for entry in default_data.values()]
total_bad = sum(bad_values)
latest_value = bad_values[-1] if bad_values else None

print("Data Values:", bad_values)
print("Total Bad:", total_bad)
print("Latest Value:", latest_value)

data_to_send = {
    'bad': total_bad
}

laravel_api_url = "http://192.168.1.22:8000/api/post-count"
headers = {'Content-Type': 'application/json'}
response = requests.post(laravel_api_url, json=data_to_send, headers=headers)

if response.status_code == 200:
    result = response.json()
    if 'message' in result and result['message'] == 'OK':
        print("Data sent successfully.")
    else:
        print("Error in Laravel API response:", result)
else:
    print("HTTP Request Error:", response.status_code)
