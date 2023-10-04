import requests

# Replace with the IP address of your laptop running Flask
flask_api_url = "http://192.168.1.26:8000/api/companies"

query = "SELECT * FROM users"
data = {"query": query}

response = requests.get(flask_api_url, json=data)

if response.status_code == 200:
    result = response.json()
    print(result)
else:
    print("HTTP Request Error:", response.status_code)

