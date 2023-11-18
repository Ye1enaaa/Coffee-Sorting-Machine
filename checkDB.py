import sqlite3

# Step 1: Connect to the SQLite database
conn = sqlite3.connect('bean_loggerist.db')
cursor = conn.cursor()

# Step 2: Execute a query to fetch data from the table
cursor.execute("SELECT * FROM bean_counts_data")

# Step 3: Check if any rows are returned
data = cursor.fetchall()
if data:
    print("Data is stored in the database.")
    # You can also process or print the data if needed
    print(data)
else:
    print("No data found in the database.")

# Step 4: Close the connection
conn.close()
