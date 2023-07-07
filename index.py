from keras.models import load_model
import cv2
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the first model
model1 = load_model("keras_model.h5", compile=False)

# Load the second model
model2 = load_model("keras_model.h5", compile=False)

# Load the labels for model 1
class_names1 = open("labels.txt", "r").readlines()

# Load the labels for model 2
class_names2 = open("labels.txt", "r").readlines()

# Initialize two cameras
camera1 = cv2.VideoCapture(0)  # First camera
camera2 = cv2.VideoCapture(2)  # Second camera

bad_beans_count = 0  # Counter for consecutive bad beans

while True:
    # Read frames from both cameras
    ret1, image1 = camera1.read()
    ret2, image2 = camera2.read()

    # Resize and display the images from both cameras
    image1 = cv2.resize(image1, (224, 224), interpolation=cv2.INTER_AREA)
    image2 = cv2.resize(image2, (224, 224), interpolation=cv2.INTER_AREA)

    cv2.imshow("Webcam Image 1", image1)
    cv2.imshow("Webcam Image 2", image2)

    # Process images from camera 1
    image1 = np.asarray(image1, dtype=np.float32).reshape(1, 224, 224, 3)
    image1 = (image1 / 127.5) - 1
    prediction1 = model1.predict(image1)
    index1 = np.argmax(prediction1)
    class_name1 = class_names1[index1]
    confidence_score1 = prediction1[0][index1]

    # Process images from camera 2
    image2 = np.asarray(image2, dtype=np.float32).reshape(1, 224, 224, 3)
    image2 = (image2 / 127.5) - 1
    prediction2 = model2.predict(image2)
    index2 = np.argmax(prediction2)
    class_name2 = class_names2[index2]
    confidence_score2 = prediction2[0][index2]

    if class_name1.strip() == "1 Bad":  # Check for "1 Bad" label for camera 1
        bad_beans_count += 1
    else:
        bad_beans_count = 0

    if class_name2.strip() == "1 Bad":  # Check for "1 Bad" label for camera 2
        bad_beans_count += 1
    else:
        bad_beans_count = 0

    print("Camera 1 - Class:", class_name1.strip()[2:])
    print("Camera 1 - Confidence Score:", str(np.round(confidence_score1 * 100))[:-2], "%")

    print("Camera 2 - Class:", class_name2.strip()[2:])
    print("Camera 2 - Confidence Score:", str(np.round(confidence_score2 * 100))[:-2], "%")

    if bad_beans_count >= 5:
        print("Actuators on")

    # Listen to the keyboard for presses.
    keyboard_input = cv2.waitKey(1)

    # 27 is the ASCII for the esc key on your keyboard.
    if keyboard_input == 27:
        break

# Release camera objects
camera1.release()
camera2.release()

# Close all windows
cv2.destroyAllWindows()
