import sqlite3
import requests

# Connect to the SQLite database
conn = sqlite3.connect("bean_loggerist.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM bean_counts_data")
    rows = cursor.fetchall()
    #data_to_send = []
    total_good = 0
    total_bad = 0
    for row in rows:
        #id, bean_type, count = row
        good_value = row[1]
        bad_value = row[2]
        
        #print(row[0])
        #print(good_value)
        #print(bad_value)
        
        total_good += good_value
        total_bad += bad_value
        
        print(total_bad)
        data_to_send = {
            'good': good_value,
            'bad': bad_value
        }

    # Define the URL of your Laravel backend API endpoint
    laravel_api_url = "http://192.168.1.26:8000/api/post-count"
    headers = {'Content-Type': 'application/json'}
    # Send a POST request to the Laravel API
    response = requests.post(laravel_api_url, json=data_to_send, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if 'message' in result and result['message'] == 'OK':
            print("Data sent successfully to Laravel backend.")
        else:
            print("Error in Laravel API response:", result)
    else:
        print("HTTP Request Error:", response.status_code)

except sqlite3.Error as e:
    print("SQLite error:", e)

finally:
    conn.close()
