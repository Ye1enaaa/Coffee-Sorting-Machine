import numpy as np
#import RPi.GPIO as GPIO
from keras.models import load_model
import time
from skimage import transform
import matplotlib.pyplot as plt

# Load the model
model = load_model("models/keras_mode11.h5", compile=False)

# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(18, GPIO.OUT)

try:
    while True:
        # Simulate video capture (replace this with your actual video capture code)
        # For Raspberry Pi, you might consider using picamera or another library.
        # For simplicity, I'm using a black image.
        image = np.zeros((480, 640, 3), dtype=np.uint8)

        # Resize the image using scikit-image
        image = transform.resize(image, (224, 224), mode='constant', anti_aliasing=True)

        # Display the captured frame using matplotlib
        plt.imshow(image)
        plt.show(block=False)
        plt.pause(0.01)

        image = image.reshape(1, 224, 224, 3).astype(np.float32)

        image = (image / 127.5) - 1

        # Predict the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names1[index].strip()
        confidence_score = prediction[0][index]

        if class_name == "1 Bad":
            #GPIO.output(18, GPIO.LOW)
            print("Hello")
        if class_name == "0 Good" or class_name == "2 Neutral":
            #GPIO.output(18, GPIO.HIGH)
            print("Hello")
        time.sleep(1)

finally:
    #GPIO.cleanup()
    print('Hii')