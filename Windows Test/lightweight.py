import cv2
import numpy as np
import RPi.GPIO as GPIO
from keras.models import load_model
import time
# Load the model
model = load_model("models/keras_mode11.h5", compile=False)

# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)

camera = cv2.VideoCapture(0)

try:
    while True:
        ret, image = camera.read()

        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        
        # Display the captured frame
        cv2.imshow("Capture Beans", image)

        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

        image = (image / 127.5) - 1

        # Predict the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names1[index].strip()
        confidence_score = prediction[0][index]

        if class_name == "1 Bad":
            GPIO.output(18, GPIO.LOW)
        if class_name == "0 Good" or class_name == "2 Neutral":
            GPIO.output(18, GPIO.HIGH)

        keyboard_input = cv2.waitKey(1)

        if keyboard_input == 27:
            break
        time.sleep(1)
finally:
    GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
