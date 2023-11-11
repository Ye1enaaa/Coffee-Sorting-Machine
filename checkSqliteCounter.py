import sqlite3

conn = sqlite3.connect("bean_loggerist.db")
cursor = conn.cursor()

#cursor = conn.cursor

try:
    cursor.execute(
    "SELECT * FROM bean_counts_data")
    
    rows = cursor.fetchall()
    #rows =cursor.fetchall()
    
    #rows = cursor
    
    #rows
    
    print(rows)
    #print("-" * 40)
    #for row in rows:
     #   print(f"{row[0]:2} | {row[1]} | {row[2]}")

except sqlite3.Error as e:
    print("SQLite error:",e)
    
finally:
    conn.close()
