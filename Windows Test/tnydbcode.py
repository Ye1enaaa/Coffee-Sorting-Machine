import cv2
import numpy as np
from keras.models import load_model
from tinydb import TinyDB
import time
# Load the model
model = load_model("models/keras_mode11.h5", compile=False)

# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

# Database Initialization
db = TinyDB('bean_tnydb.json')

camera = cv2.VideoCapture(0)

# Set the desired resolution for the camera
camera.set(3, 224)  # Width
camera.set(4, 224)  # Height

try:
    while True:
        _, image = camera.read()

        # Resize the image
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Display the captured frame
        cv2.imshow("Capture Beans", image)

        # Preprocess the image
        image = np.asarray(image, dtype=np.float32)
        image = (image / 127.5) - 1
        image = np.expand_dims(image, axis=0)

        # Predict the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names1[index].strip()
        confidence_score = prediction[0][index]

        if class_name == "1 Bad":
            print("Bad bean detected with confidence:", confidence_score*100)

            # Insert bad bean information into TinyDB
            db.insert({'status': 'bad'})

        elif class_name == "0 Good" or class_name == "2 Neutral":
            print("Good or neutral bean detected with confidence:", confidence_score*100)

        keyboard_input = cv2.waitKey(1)

        if keyboard_input == 27:
            break

        time.sleep(1)

finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()
