print("AI Demo")
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import cv2
import time
import os

execution_path = os.getcwd()
cam = cv2.VideoCapture(0)
# Load the model
model = load_model('AI\keras_model.h5')

def capture_image():
    start_time = time.time()
    ret, frame = cam.read()
    fpsInfo = "FPS: " + str(1.0 / (time.time() - start_time)) 
    print(fpsInfo)

    cv2.putText(frame, fpsInfo, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)
    cv2.imwrite("img_detect.png", frame)

def ai_detection():
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # Replace this with the path to your image
    image = Image.open('img_detect.png').convert('RGB')
    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    print("Predict: " + str(prediction))
    result_ai = prediction[0]
    max_value = result_ai[0]
    max_index = 0
    for i in range(0, len(result_ai)):
        if max_value < result_ai[i]:
            max_value = result_ai[i]
            max_index = i
    print(max_index, result_ai[max_index])
    return max_index, int(result_ai[max_index] * 100)

while True:
    capture_image()
    ai_detection()
    time.sleep(5)
     # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()