import cv2
import numpy as np
#import RPi.GPIO as GPIO
from keras.models import load_model
import time
import sqlite3
from imutils import perspective
from imutils import contours
import imutils
from scipy.spatial.distance import euclidean

# Constants
MODEL_PATH = "keras_model.h5"
LABELS_PATH = "labels.txt"
BAD_THRESHOLD = 80  # Set the confidence threshold for "Bad" class
GOOD_THRESHOLD = 5

# Load the model and labels
model = load_model(MODEL_PATH, compile=False)
class_names = [line.strip() for line in open(LABELS_PATH, "r")]

# Set up GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(18, GPIO.OUT)

# Create the database and table
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
    camera = cv2.VideoCapture(2)

    while True:
        ret, frame = camera.read()
        size = cv2.resize(frame, (224, 224))
        image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        cv2.imshow("Quality", image)

        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(size, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (9, 9), 0)

        edged = cv2.Canny(blur, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # Apply a threshold to the image to separate the objects from the background
        ret, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for cnt in cnts:
            (x, y, w, h) = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            dist_in_pixel = euclidean((x, 0), (x + w, 0))
            dist_in_cm = 2
            pixel_per_cm = dist_in_pixel / dist_in_cm

            width = w - x
            ratio_px_mm = 8000 / 10
            mm = width / ratio_px_mm
            cm = mm / 10

            wid = euclidean((x, 0), (y, 0)) / pixel_per_cm
            ht = euclidean((y, 0), (w, 0)) / pixel_per_cm

            if 3000 < area < 4700:
                if class_name == "1 Bad" and confidence_score > BAD_THRESHOLD / 100:
                    # Trigger GPIO or take other action
                    print("Bad bean detected with high confidence!")
                    # GPIO.output(18, GPIO.HIGH)
                    bad_consecutive_count += 1
                    good_consecutive_count = 0

                elif class_name == "0 Good":
                    #GPIO.output(18, GPIO.LOW)
                    good_consecutive_count += 1
                    bad_consecutive_count = 0
        
                else:
                    #GPIO.output(18, GPIO.LOW)
                    good_consecutive_count = 0
                    bad_consecutive_count = 0

                cv2.putText(size, "{}".format(class_name[2:]), (x + 20, y +  50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
                cv2.putText(size, "{:.1f} w".format(wid), (int(x) - 50, int(y) + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.putText(size, "{:.1f} L".format(ht), (int(y) + 20 , int(w) - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.rectangle(size, (x, y), (x + w, y + h), (0, 0, 255), 2)
                print("size is bad")
                print(area)

            elif area > 4700:
                if class_name == "1 Bad" and confidence_score > BAD_THRESHOLD / 100:
                    # Trigger GPIO or take other action
                    print("Bad bean detected with high confidence!")
                    # GPIO.output(18, GPIO.HIGH)
                    bad_consecutive_count += 1
                    good_consecutive_count = 0

                elif class_name == "0 Good":
                    #GPIO.output(18, GPIO.LOW)
                    good_consecutive_count += 1
                    bad_consecutive_count = 0
        
                else:
                    #GPIO.output(18, GPIO.LOW)
                    good_consecutive_count = 0
                    bad_consecutive_count = 0
                cv2.putText(size, "{}".format(class_name[2:]), (x + 20, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
                cv2.putText(size, "{:.1f} w".format(wid), (int(x) - 15, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.putText(size, "{:.1f} L".format(ht), (int(y) + 120, int(w)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                cv2.rectangle(size, (x, y), (x + w, y + h), (255, 0, 0), 2)
                print("size is good")
                print(area)

        print(f"Class: {class_name}")
        print(f"Confidence Score: {confidence_score * 100:.2f}%")

        # cv2.imshow("Frame", frame)
        cv2.imshow("Size", size)
        cv2.imshow("Thresh", thresh)
        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break

finally:
    # Combine consecutive database inserts
    with sqlite3.connect("bean_loggerist.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO bean_counts_data(good, bad) VALUES (?, ?);''', (good_consecutive_count, bad_consecutive_count))
        conn.commit()

    #GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()