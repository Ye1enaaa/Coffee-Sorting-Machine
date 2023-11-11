import cv2
import numpy as np
import RPi.GPIO as GPIO
from keras.models import load_model
import time
import sqlite3
# Load the model
model = load_model("keras_test_one.h5", compile=False)

# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)

#GPIO.output(18, GPIO.HIGH)

# CAMERA can be 0 or 1 based on the default camera of your computer
camera = cv2.VideoCapture(0)

#bad_beans_count = 0  # Counter for consecutive bad beans
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
    while True:
        # Grab the web camera's image.
        ret, image = camera.read()

        # Resize the raw image into (224-height,224-width) pixels
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        
        # Display the captured frame
        cv2.imshow("Capture Beans", image)

        # Make the image a numpy array and reshape it to the model's input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

        # Normalize the image array
        image = (image / 127.5) - 1

        # Predict the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        if class_name == "1 Bad":
            GPIO.output(18, GPIO.HIGH)
            #if current_bean_type != "Bad":
                #bad_consecutive_count = 0
            bad_consecutive_count += 1
            good_consecutive_count = 0
            #current_bean_type = 'Bad'
        if class_name == "0 Good":
            #bad_beans_count = 0
            GPIO.output(18, GPIO.LOW)
            #if current_bean_type != "Good":
                #consecutive_count = 0
            good_consecutive_count += 1
            bad_consecutive_count = 0
            #current_bean_type = 'Good'
        if class_name == "2 Neutral":
            #bad_beans_count = 0
            GPIO.output(18, GPIO.LOW)
            good_consecutive_count = 0
            bad_consecutive_count = 0
        # Print prediction and confidence score
        print("Class:", class_name[2:])
        #print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

        if bad_consecutive_count >= 5:
           # cursor.execute("SELECT count FROM bean_counts WHERE bean_type = ?", (current_bean_type,))
            #result = cursor.fetchone()
            #if result:
            #   current_count = result[0]
            #    current_count += 1
            #    cursor.execute("UPDATE bean_counts SET count = ? WHERE bean_type =?", (current_count, current_bean_type))
            #else:
                #cursor.execute("INSERT INTO bean_counts(bean_type,count) VALUES (?, 1)", (current_bean_type,))
            insert_data_query = '''
            INSERT INTO bean_counts_data(good, bad) VALUES (?,?);
            '''
            bean_value = (0,1)
            cursor.execute(insert_data_query, bean_value)
            print("Bad bean added")
            conn.commit()
            bad_consecutive_count = 0
        if good_consecutive_count >= 5:
           # cursor.execute("SELECT count FROM bean_counts WHERE bean_type = ?", (current_bean_type,))
            #result = cursor.fetchone()
            #if result:
            #   current_count = result[0]
            #    current_count += 1
            #    cursor.execute("UPDATE bean_counts SET count = ? WHERE bean_type =?", (current_count, current_bean_type))
            #else:
                #cursor.execute("INSERT INTO bean_counts(bean_type,count) VALUES (?, 1)", (current_bean_type,))
            insert_data_query = '''
            INSERT INTO bean_counts_data(good, bad) VALUES (?,?);
            '''
            bean_value = (1,0)
            cursor.execute(insert_data_query, bean_value)
            print("Good bean added")
            conn.commit()
            good_consecutive_count = 0
        

        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break

finally:
    GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
    conn.close()
