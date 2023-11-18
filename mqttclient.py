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

# Load the model and labels
model = load_model(MODEL_PATH, compile=False)
class_names = [line.strip() for line in open(LABELS_PATH, "r")]

# MQTT Broker address (replace with the IP address of your Raspberry Pi)
broker_address = "192.168.1.23"

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
    camera = cv2.VideoCapture(2)

    while True:
        ret, image = camera.read()
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        cv2.imshow("Capture Beans", image)

        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        if class_name == "1 Bad":
            #and confidence_score > BAD_THRESHOLD / 100: 
            #send_command('activate')
            bad_consecutive_count += 1
            #good_consecutive_count = 0
        elif class_name == "0 Good":
            send_command('deactivate')
            good_consecutive_count += 1
            bad_consecutive_count = 0
        else:
            send_command('deactivate')
            good_consecutive_count = 0
            bad_consecutive_count = 0

        if bad_consecutive_count == 5:
            send_command('activate')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO bean_counts_data(bad) VALUES (?);''', (1,))
            conn.commit()
            class_name == "0 Good"
            bad_consecutive_count = 0
        if bad_consecutive_count >= 5:
            send_command('deactivate')
            class_name == "0 Good"
            bad_consecutive_count = 0
        print(f"Class: {class_name}")
        print(f"Confidence Score: {confidence_score * 100:.2f}%")

        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break
        time.sleep(0.7)
finally:
    # Combine consecutive database inserts
    #with sqlite3.connect("bean_loggerist.db") as conn:
        #cursor = conn.cursor()
        #cursor.execute('''INSERT INTO bean_counts_data(bad) VALUES (?);''', (bad_consecutive_count))
        #conn.commit()

    camera.release()
    cv2.destroyAllWindows()
