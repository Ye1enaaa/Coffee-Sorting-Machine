import cv2
import numpy as np
#import RPi.GPIO as GPIO
from keras.models import load_model
import time
import sqlite3

# Load the model
model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(18, GPIO.OUT)

camera = cv2.VideoCapture(0)

conn = sqlite3.connect("bean_loggerist.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS bean_counts_data(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  good FLOAT,
                  bad FLOAT
                )''')
conn.commit()

try:
    bad_consecutive_count = 0
    good_consecutive_count = 0
    current_bean_type = None
    scanning_enabled = True  # Variable to control scanning

    while True:
        ret, image = camera.read()
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        cv2.imshow("Capture Beans", image)

        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        if class_name == "1 Bad":
            #GPIO.output(18, GPIO.HIGH)
            bad_consecutive_count += 1
            good_consecutive_count = 0
        elif class_name == "0 Good":
            #GPIO.output(18, GPIO.LOW)
            good_consecutive_count += 1
            bad_consecutive_count = 0
        elif class_name == "2 Neutral":
            #GPIO.output(18, GPIO.LOW)
            good_consecutive_count = 0
            bad_consecutive_count = 0

        print("Class:", class_name[2:])

        if bad_consecutive_count >= 5:
            insert_data_query = '''INSERT INTO bean_counts_data(good, bad) VALUES (?,?);'''
            bean_value = (0, 1)
            cursor.execute(insert_data_query, bean_value)
            print("Bad bean added")
            conn.commit()
            bad_consecutive_count = 0
        if good_consecutive_count >= 5:
            insert_data_query = '''INSERT INTO bean_counts_data(good, bad) VALUES (?,?);'''
            bean_value = (1, 0)
            cursor.execute(insert_data_query, bean_value)
            print("Good bean added")
            conn.commit()
            good_consecutive_count = 0
            
            # Disable scanning for 2 seconds
            scanning_enabled = False
            pause_start_time = time.time()
            while time.time() - pause_start_time < 2:
                pass
            scanning_enabled = True

        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break

finally:
    #GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
    conn.close()
