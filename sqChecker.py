import time
import sqlite3

dbConn = sqlite3.connect('sqChecker.db')
cursor = dbConn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tryDb 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        bean INTEGER DEFAULT 0,
    );''')


while True:
    cursor.execute("SELECT bean FROM tryDb ORDER BY id DESC LIMIT 1")
    last_bad_beans_count = cursor.fetchone()
    if last_bad_beans_count:
        total_bad_beans = last_bad_beans_count[0] + 1
    else:
        total_bad_beans = 1

    # Step 2b: Insert the new bad bean count into the database
    cursor.execute("INSERT INTO tryDb (bean) VALUES (?)", (total_bad_beans))

    time.sleep(2.0)


    # 27 is the ASCII for the esc key on your keyboard.
    
    break
dbConn.close()