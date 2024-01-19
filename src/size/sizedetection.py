import cv2
import numpy as np
from keras.models import load_model
from tinydb import TinyDB, Query
import time
import subprocess

# Load the models
quality_model = load_model("models/keras_model_quality.h5", compile=False)
size_model = load_model("models/keras_model_size.h5", compile=False)

camera = cv2.VideoCapture(0)

# Load the labels for quality model
class_names_quality = open("labels_quality.txt", "r").readlines()

# Load the labels for size model
class_names_size = open("labels_size.txt", "r").readlines()

# Database Initialization
db = TinyDB('tnydb.json')

badConsecutive = 0

try:
    while True:
        _, image = camera.read()

        # Resize the image
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Preprocess the image for quality model
        image_quality = np.asarray(image, dtype=np.float32)
        image_quality = (image_quality / 127.5) - 1

        # Preprocess the image for size model
        image_size = np.asarray(image, dtype=np.float32)
        image_size = (image_size / 127.5) - 1

        # Predict the quality model
        prediction_quality = quality_model.predict(np.expand_dims(image_quality, axis=0))
        index_quality = np.argmax(prediction_quality)
        class_name_quality = class_names_quality[index_quality].strip()
        confidence_score_quality = np.round(prediction_quality[0][index_quality] * 100)

        # Predict the size model
        prediction_size = size_model.predict(np.expand_dims(image_size, axis=0))
        index_size = np.argmax(prediction_size)
        class_name_size = class_names_size[index_size].strip()
        confidence_score_size = np.round(prediction_size[0][index_size] * 100)

        # Logic for GPIO control based on quality and size
        if (
            (class_name_quality == "1 Bad" and confidence_score_quality > 80)
            or (class_name_quality == "0 Good" and confidence_score_quality < 50)
        ) and (
            (class_name_size == "1 Large" and confidence_score_size > 80)
            or (class_name_size == "0 Small" and confidence_score_size < 50)
        ):
            print("Bad quality and large size detected with confidence:", confidence_score_quality * confidence_score_size)
            # GPIO.output(18, GPIO.HIGH)
            badConsecutive += 1

        elif class_name_quality == "0 Good" and class_name_size == "0 Small":
            print("Good quality and small size detected with confidence:", confidence_score_quality * confidence_score_size)
            # GPIO.output(18, GPIO.HIGH)

        keyboard_input = cv2.waitKey(1)

        if badConsecutive >= 3:
            existing_data = db.all()[0]['data']
            existing_data['bad'] += 1
            db.update({'data': existing_data}, Query().data.exists())
            badConsecutive = 0

        if keyboard_input == 27:
            break

except Exception as e:
    print('Error', e)
    print('Rebooting...')
    subprocess.run(["sudo", "reboot"])

finally:
    # Release resources
    camera.release()
    cv2.destroyAllWindows()
