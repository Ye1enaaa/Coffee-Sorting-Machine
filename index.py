import tkinter as tk
import cv2
import numpy as np
import RPi.GPIO as GPIO
from keras.models import load_model
import time
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14, GPIO.OUT)

# CAMERA can be 0 or 1 based on the default camera of your computer
camera = cv2.VideoCapture(0)

bad_beans_count = 0  # Counter for consecutive bad beans

def start_scanning():
    global bad_beans_count
    global neut_good_beans_count
    while True:
        # Grab the web camera's image.
        ret, image = camera.read()

        # Resize the raw image into (224-height,224-width) pixels
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window
        cv2.imshow("Webcam Image", image)

        # Make the image a numpy array and reshape it to the model's input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

        # Normalize the image array
        image = (image / 127.5) - 1

        # Predict the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        if class_name.strip() == "1 Bad":  # Check for "1 Bad" label
            bad_beans_count += 1
        else:
            bad_beans_count = 0
        
        if class_name.strip() == "0 Good" or class_name.strip() == "2 Neutral":
            GPIO.output(14, GPIO.LOW)
            #bad_beans_count = 0
#         if class_name.strip() == "2 Neutral":
#             neut_good_beans_count = 1
#             #bad_beans_count = 0
        # Print prediction and confidence score
        print("Class:", class_name.strip()[2:])
        print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

        if bad_beans_count >= 5:
            print("Actuators on")
            GPIO.output(14, GPIO.HIGH)
            bad_beans_count = 0
            # code for actuators
        if bad_beans_count == 2:
            GPIO.output(14, GPIO.LOW)
            #either butangan ni dirig time.sleep()
#         if neut_good_beans_count == 1:
#             GPIO.output(14, GPIO.LOW)
        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break

    camera.release()
    cv2.destroyAllWindows()

# Create the main application window
root = tk.Tk()
root.geometry("400x300")  # Set the window size (width x height)

# Create a function to handle the button click event
def button_click():
    label.config(text="Scanning process started!")
    start_scanning()

# Create a label and a button in the window
label = tk.Label(root, text="Click the button to start scanning!")
label.pack(pady=20)
button = tk.Button(root, text="Start Scanning", command=button_click)
button.pack()

# Start the Tkinter event loop
root.mainloop()
GPIO.cleanup()
