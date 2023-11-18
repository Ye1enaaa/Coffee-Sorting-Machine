import cv2
import numpy as np
#import RPi.GPIO as GPIO
from keras.models import load_model
import time
import sqlite3

# Constants
MODEL_PATH_CAM1 = "keras_model.h5"
MODEL_PATH_CAM2 = "keras_model.h5"
LABELS_PATH = "labels.txt"
BAD_THRESHOLD = 5
GOOD_THRESHOLD = 5

# Load the models and labels
model_cam1 = load_model(MODEL_PATH_CAM1, compile=False)
model_cam2 = load_model(MODEL_PATH_CAM2, compile=False)
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

    # Initialize two cameras
    camera1 = cv2.VideoCapture(0)
    camera2 = cv2.VideoCapture(2)

    while True:
        # Read frames from both cameras
        ret1, image1 = camera1.read()
        ret2, image2 = camera2.read()

        # Resize and process images from camera 1
        image1 = cv2.resize(image1, (224, 224), interpolation=cv2.INTER_AREA)
        image1 = np.asarray(image1, dtype=np.float32).reshape(1, 224, 224, 3)
        image1 = (image1 / 127.5) - 1

        prediction_cam1 = model_cam1.predict(image1)
        index_cam1 = np.argmax(prediction_cam1)
        class_name_cam1 = class_names[index_cam1]
        confidence_score_cam1 = prediction_cam1[0][index_cam1]

        # Resize and process images from camera 2
        image2 = cv2.resize(image2, (224, 224), interpolation=cv2.INTER_AREA)
        image2 = np.asarray(image2, dtype=np.float32).reshape(1, 224, 224, 3)
        image2 = (image2 / 127.5) - 1

        prediction_cam2 = model_cam2.predict(image2)
        index_cam2 = np.argmax(prediction_cam2)
        class_name_cam2 = class_names[index_cam2]
        confidence_score_cam2 = prediction_cam2[0][index_cam2]

        # Combine images (adjust the concatenation axis based on your camera arrangement)
        combined_image = np.hstack((image1[0], image2[0]))
        #print("Combined Image Shape:", combined_image.shape)
        cv2.imshow("Capture Beans", combined_image)

        if class_name_cam1 == "1 Bad" or class_name_cam2 == "1 Bad":
            #GPIO.output(18, GPIO.HIGH)
            print('Bad')
            bad_consecutive_count += 1
            good_consecutive_count = 0
        elif class_name_cam1 == "0 Good" or class_name_cam2 == "0 Good":
            #GPIO.output(18, GPIO.LOW)
            print('Good')
            good_consecutive_count += 1
            bad_consecutive_count = 0
        else:
            #GPIO.output(18, GPIO.LOW)
            print('Neutral')
            good_consecutive_count = 0
            bad_consecutive_count = 0

        print("Class Camera 1:", class_name_cam1)
        print("Confidence Score Camera 1:", f"{confidence_score_cam1 * 100:.2f}%")

        print("Class Camera 2:", class_name_cam2)
        print("Confidence Score Camera 2:", f"{confidence_score_cam2 * 100:.2f}%")

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
    camera1.release()
    camera2.release()
    cv2.destroyAllWindows()
    conn.close()
