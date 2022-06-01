import logging
import sentry_sdk
import time
import cv2
import numpy as np
from PIL import Image, ImageOps
from keras.models import load_model
sentry_sdk.init(
    "https://df1d0f6c65214be9b14737b8d26cde07@o1266351.ingest.sentry.io/6458960",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1
)


def ai_detection(cam, model):
    ret, frame = cam.read()
    cv2.imwrite("img_detect.png", frame)
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # Replace this with the path to your image
    image = Image.open('img_detect.png').convert('RGB')
    # resize the image to a 224x224 with the same strategy as in TM2:
    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    # turn the image into a numpy array
    image_array = np.asarray(image)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    result_ai = prediction[0]
    max_value = result_ai[0]
    max_index = 0
    for i in range(0, len(result_ai)):
        if max_value < result_ai[i]:
            max_value = result_ai[i]
            max_index = i
    if max_index == 0:
        return ({"Status": "Healthy", "Percentage": int(result_ai[max_index] * 100)})
    else:
        return ({"Status": "Sick", "Percentage": int(result_ai[max_index] * 100)})


def start(cam, model):
    try:
        return ai_detection(cam, model)
            # time.sleep(5)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
    except Exception as general_exception:
        sentry_sdk.capture_exception(general_exception)
        logging.exception(general_exception)
