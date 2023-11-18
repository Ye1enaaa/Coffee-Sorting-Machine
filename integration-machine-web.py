import sqlite3
import requests


conn = sqlite3.connect("bean_loggerist.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM bean_counts_data")
    rows = cursor.fetchall()
    data_value = []
    total_bad = 0

    for row in rows:
        # Assuming the structure of each row is a list
        last_value = row[-1] if row else None

        # Append the last value to data_value list
        data_value.append(last_value)

        # Update total_bad count if the last value is not None
        if last_value is not None:
            total_bad += last_value

    # Get the latest value
    latest_value = data_value[-1] if data_value else None

    print("Data Values:", data_value)
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
            print("Data sent successfully to Laravel backend.")
        else:
            print("Error in Laravel API response:", result)
    else:
        print("HTTP Request Error:", response.status_code)

except sqlite3.Error as e:
    print("SQLite error:", e)

finally:
    conn.close()
