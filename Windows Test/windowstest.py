import cv2
import numpy as np
from keras.models import load_model
import time
import sqlite3

# First Camera Settings
MODEL_PATH = "models/keras_mode11.h5"
LABELS_PATH = "labels.txt"
BAD_THRESHOLD = 80  # Set the confidence threshold for "Bad" class
GOOD_THRESHOLD = 5

model = load_model(MODEL_PATH, compile=False)
class_names = [line.strip() for line in open(LABELS_PATH, "r")]

# Second Camera Settings
MODEL_PATH_2 = "models/keras_mode11.h5"


model2 = load_model(MODEL_PATH_2, compile=False)
class_names_2 = [line.strip() for line in open(LABELS_PATH, "r")]

# Database Initialization
with sqlite3.connect("bean_loggerist.db") as conn:
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

    # First Camera Initialization
    camera = cv2.VideoCapture(0)

    # Second Camera Initialization
    camera2 = cv2.VideoCapture(1)  # Use the appropriate camera index for the second camera.

    while True:
        # First Camera Processing
        ret, image = camera.read()
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        cv2.imshow("Capture Beans", image)

        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        if class_name == "1 Bad" and confidence_score > BAD_THRESHOLD / 100:
            print("First Camera - Bad bean detected with high confidence!")
            bad_consecutive_count += 1
            good_consecutive_count = 0
        elif class_name == "0 Good":
            good_consecutive_count += 1
            bad_consecutive_count = 0
        else:
            good_consecutive_count = 0
            bad_consecutive_count = 0

        print(f"First Camera - Class: {class_name}")
        print(f"First Camera - Confidence Score: {confidence_score * 100:.2f}%")

        # Second Camera Processing
        ret2, image2 = camera2.read()
        image2 = cv2.resize(image2, (224, 224), interpolation=cv2.INTER_AREA)
        cv2.imshow("Capture Beans", image2)

        image2 = np.asarray(image2, dtype=np.float32).reshape(1, 224, 224, 3)
        image2 = (image2 / 127.5) - 1

        prediction2 = model2.predict(image2)
        index2 = np.argmax(prediction2)
        class_name_2 = class_names_2[index2]
        confidence_score_2 = prediction2[0][index2]

        print(f"Second Camera - Class: {class_name_2}")
        print(f"Second Camera - Confidence Score: {confidence_score_2 * 100:.2f}%")

        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break
        time.sleep(1.5)
finally:
    # Combine consecutive database inserts
    # with sqlite3.connect("bean_loggerist.db") as conn:
    #     cursor = conn.cursor()
    #     cursor.execute(
    #         '''INSERT INTO bean_counts_data(good, bad) VALUES (?, ?);''', (good_consecutive_count, bad_consecutive_count))
    #     conn.commit()

    # Release resources for both cameras
    camera.release()
    camera2.release()
    cv2.destroyAllWindows()
