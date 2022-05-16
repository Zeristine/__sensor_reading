from pickle import TRUE
import time
import threading
from numpy import append
import schedule
import queue
import crc_modbus_16_calculation as chkSum
from server_api.api_handler import APIHandler
from kafka_connect import KafkaHandler
import modbus_serial_connect as sensor_connect

# region import AI
import cv2
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

cam = cv2.VideoCapture(0)
model = load_model('AI\keras_model.h5')


def capture_image():
    ret, frame = cam.read()
    cv2.imwrite("img_detect.png", frame)


def ai_detection():
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
    print("Predict: " + str(prediction))
    result_ai = prediction[0]
    max_value = result_ai[0]
    max_index = 0
    for i in range(0, len(result_ai)):
        if max_value < result_ai[i]:
            max_value = result_ai[i]
            max_index = i
    if max_index == 0:
        pub_response({"Status": "Healthy", "Percentage": int(
            result_ai[max_index] * 100)}, "camera_data")
    else:
        pub_response({"Status": "Sick", "Percentage": int(
            result_ai[max_index] * 100)}, "camera_data")
    #print(max_index, result_ai[max_index])
    return max_index, int(result_ai[max_index] * 100)
# endregion


list_request = []


def push_sensor_request():
    print("Push request to sensor")
    if(len(list_request) <= 0):
        fetch_api()
    if(len(list_request) > 0):
        # push to sensor
        # print(list_request)
        generate_request()


def generate_request():
    list_send = []
    for request in list_request:
        obj_request = {
            "id": request["id"],
            "requests": []
        }
        address_sensor = request["address"].split(",")
        for label in request["labels"]:
            address_label = label["address"].split(",")
            item_request = []
            item_request.append(address_sensor[0])
            item_request.append(address_sensor[1])
            item_request.append(address_label[0])
            item_request.append(address_label[1])
            # item_request.append("0x00")
            # item_request.append("0x01")
            item_request.append(address_label[2])
            item_request.append(address_label[3])
            # high_byte, low_byte = chkSum.crc_modbus_calculate(item_request)
            # item_request.append(hex(low_byte))
            # item_request.append(hex(low_byte))
            obj_request["requests"].append(
                chkSum.generate_modbus_message(item_request))
        list_send.append(obj_request)
        print("Sending")
        sensor_connect.addRequestsToQueue(list_send)


def pub_response(response, topic="sensor_data"):
    print("Pub response to Kafka")
    instanceKafka = KafkaHandler()
    instanceKafka._pub(topic, response)


def fetch_api():
    print("Fetch api data")
    instanceAPI = APIHandler()
    list_result = instanceAPI._get_request()
    global list_request
    if(len(list_request) > 0):
        for result in list_result:
            is_dup = True
            for request in list_request:
                if(request["id"] is not result["id"]):
                    is_dup = False
            if(not is_dup):
                list_request.append(result)
    else:
        list_request = list_result


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()


jobqueue = queue.Queue()

# schedule.every(1).seconds.do(jobqueue.put, fetch_api)
schedule.every(5).seconds.do(jobqueue.put, push_sensor_request)
schedule.every(5).seconds.do(jobqueue.put, ai_detection)
schedule.every(1).minutes.do(jobqueue.put, fetch_api)
if __name__ == '__main__':
    sensor_connect.startProcesses()

    # sensor_connect.initSerialModel()
    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()
    loop_forever = True
    while loop_forever:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            loop_forever = False
        # capture_image()
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    cam.release()
    cv2.destroyAllWindows()
