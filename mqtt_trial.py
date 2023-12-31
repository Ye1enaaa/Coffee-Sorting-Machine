import cv2
import numpy as np
import paho.mqtt.publish as publish
from keras.models import load_model
import time
import sqlite3

# Constants
MODEL_PATH = "keras_mode11.h5"
LABELS_PATH = "labels.txt"
BAD_THRESHOLD = 80  # Set the confidence threshold for "Bad" class
GOOD_THRESHOLD = 5
scanning_enabled = True
toggle_interval = 1  # in seconds
last_toggle_time = time.time()

# Load the model and labels
model = load_model(MODEL_PATH, compile=False)
class_names = [line.strip() for line in open(LABELS_PATH, "r")]

# MQTT Broker address (replace with the IP address of your Raspberry Pi)
broker_address = "192.168.1.3"

def send_command(command):
    publish.single("actuator/control", payload=command, hostname=broker_address)

# Set up database
with sqlite3.connect("bean_loggerist.db") as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bean_counts_data(
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      bad INTEGER
                    )''')
    conn.commit()

try:
    bad_consecutive_count = 0
    good_consecutive_count = 0
    current_bean_type = None
    camera = cv2.VideoCapture(0)

    while True:
        current_time = time.time()
        elapsed_time_since_toggle = current_time - last_toggle_time

        if elapsed_time_since_toggle >= toggle_interval:
            # Toggle the scanning process
            scanning_enabled = not scanning_enabled
            last_toggle_time = current_time

        if scanning_enabled:
            ret, image = camera.read()
            image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
            cv2.imshow("Capture Beans", image)

            image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
            image = (image / 127.5) - 1

            # Replace the following with your actual model prediction code
            prediction = model.predict(image)
            index = np.argmax(prediction)
            class_name = class_names[index]
            confidence_score = prediction[0][index]

            if class_name == "1 Bad" and confidence_score > BAD_THRESHOLD / 100:
                # Trigger GPIO on Raspberry Pi
                print("Bad bean detected with high confidence!")
                # Replace the following line with your GPIO activation code
                # send_command('activate')
                bad_consecutive_count += 1
            elif class_name == "0 Good":
                # Replace the following line with your GPIO deactivation code
                # send_command('deactivate')
                good_consecutive_count += 1
                bad_consecutive_count = 0
            else:
                # Replace the following line with your GPIO deactivation code
                # send_command('deactivate')
                good_consecutive_count = 0
                bad_consecutive_count = 0

            if bad_consecutive_count >= 2:
                # Replace the following lines with your database insertion code
                # cursor = conn.cursor()
                # cursor.execute('''INSERT INTO bean_counts_data(bad) VALUES (?);''', (1,))
                # conn.commit()
                print("Insert into database: Bad bean count reached")

            print(f"Class: {class_name}")
            print(f"Confidence Score: {confidence_score * 100:.2f}%")

        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break


finally:
    # Combine consecutive database inserts
    #with sqlite3.connect("bean_loggerist.db") as conn:
        #cursor = conn.cursor()
        #cursor.execute('''INSERT INTO bean_counts_data(bad) VALUES (?);''', (bad_consecutive_count))
        #conn.commit()

    camera.release()
    cv2.destroyAllWindows()
