from SimpleCV import Camera, Display
import numpy as np
#import RPi.GPIO as GPIO
from keras.models import load_model
import time

# Load the model
model = load_model("models/keras_mode11.h5", compile=False)

# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(18, GPIO.OUT)

camera = Camera()

display = Display()


while not display.isDone():
    image = camera.getImage()

    image = image.resize((224, 224))

    # Display the captured frame
    image.show()

    image_np = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    image_np = (image_np / 127.5) - 1

    # Predict the model
    prediction = model.predict(image_np)
    index = np.argmax(prediction)
    class_name = class_names1[index].strip()
    confidence_score = prediction[0][index]

    if class_name == "1 Bad":
        #GPIO.output(18, GPIO.LOW)
        print("HI")
    if class_name == "0 Good" or class_name == "2 Neutral":
        #GPIO.output(18, GPIO.HIGH)
        print('Hi')
    time.sleep(1)

#finally:
    #GPIO.cleanup()
    #cv2.destroyAllWindows()
