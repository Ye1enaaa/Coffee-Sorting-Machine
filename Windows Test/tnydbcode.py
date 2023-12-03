import cv2
import numpy as np
from keras.models import load_model
from tinydb import TinyDB, Query
import time
import subprocess
# Load the model
model = load_model("models/keras_mode11.h5", compile=False)
camera = cv2.VideoCapture(0)
# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

# Database Initialization
db = TinyDB('tnydb.json')

#if not db:
#    db.insert({'data': {'bad': 0}})

badConsecutive = 0
# Set the desired resolution for the camera
#camera.set(3, 224)  # Width
#camera.set(4, 224)  # Height

try:
    while True:
        _, image = camera.read()

        # Resize the image
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Display the captured frame
        #cv2.imshow("Capture Beans", image)

        # Preprocess the image
        image = np.asarray(image, dtype=np.float32)
        image = (image / 127.5) - 1
        #image = np.expand_dims(image, axis=0)

        # Predict the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names1[index].strip()
        confidence_score = np.round(prediction[0][index] * 100)

        if class_name == "1 Bad" and confidence_score > 80:
            print("Bad bean detected with confidence:", confidence_score*100)
            #GPIO.output(18,GPIO.LOW)
            # Insert bad bean information into TinyDB
            badConsecutive += 1
            existing_data = db.all()[0]['data']
            existing_data['bad'] += 1
            db.update({'data': existing_data}, Query().data.exists())

        elif class_name == "0 Good" or class_name == "2 Neutral":
            print("Good or neutral bean detected with confidence:", confidence_score*100)
            #GPIO.output(18, GPIO.HIGH)
        keyboard_input = cv2.waitKey(1)

        if badConsecutive == 4:
            existing_data = db.all()[0]['data']
            existing_data['bad'] += 1
            db.update({'data': existing_data}, Query().data.exists())
            badConsecutive = 0
        if keyboard_input == 27:
            break

        #time.sleep(1)
except Exception as e:
    print('Error', e)
    print('Rebooting...')
    subprocess.run(["sudo","reboot"])
finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()
