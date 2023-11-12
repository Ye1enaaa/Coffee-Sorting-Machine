import cv2
import numpy as np
#import RPi.GPIO as GPIO
from keras.models import load_model
import time
import sqlite3

# Constants
MODEL_PATH = "keras_test_one.h5"
LABELS_PATH = "labels.txt"
BAD_THRESHOLD = 5
GOOD_THRESHOLD = 5

# Load the model and labels
model = load_model(MODEL_PATH, compile=False)
class_names = [line.strip() for line in open(LABELS_PATH, "r")]

# Set up GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(18, GPIO.OUT)

# Create the database and table
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
    camera = cv2.VideoCapture(0)

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
            #GPIO.output(18, GPIO.HIGH)
            print('Bad')
            bad_consecutive_count += 1
            good_consecutive_count = 0
        elif class_name == "0 Good":
            print('Good')
            #GPIO.output(18, GPIO.LOW)
            good_consecutive_count += 1
            bad_consecutive_count = 0
        else:
            #GPIO.output(18, GPIO.LOW)
            print('Neutral')
            good_consecutive_count = 0
            bad_consecutive_count = 0

        print("Class:", class_name)
        print("Confidence Score:", f"{confidence_score * 100:.2f}%")

        if bad_consecutive_count >= BAD_THRESHOLD:
            cursor.execute('''INSERT INTO bean_counts_data(good, bad) VALUES (?, ?);''', (0, 1))
            conn.commit()
            print("Bad bean added")
            bad_consecutive_count = 0

        if good_consecutive_count >= GOOD_THRESHOLD:
            cursor.execute('''INSERT INTO bean_counts_data(good, bad) VALUES (?, ?);''', (1, 0))
            conn.commit()
            print("Good bean added")
            good_consecutive_count = 0

        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break

finally:
    #GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
    conn.close()
