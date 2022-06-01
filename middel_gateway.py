import os
import handler.ai_detection as AI
from keras.models import load_model
import cv2
from pickle import TRUE
import time
import threading
from numpy import append
from requests import request
import schedule
import queue
import utils.crc_modbus_16_calculation as chkSum
import handler.api_handler as APIHandler
import handler.kafka_handler as KafkaHandler
import handler.modbus_serial_connect as sensor_connect
import sentry_sdk
import logging
import serial.serialutil as serial_util
import json
from collections import deque

sentry_sdk.init(
    "https://df1d0f6c65214be9b14737b8d26cde07@o1266351.ingest.sentry.io/6458960",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1
)
# region import AI
execution_path = os.getcwd()
cam = cv2.VideoCapture(0)
# Load the model
model = load_model('resources\model_ai\keras_model.h5')
# endregion

list_request = []
jobqueue = queue.Queue()
response_queue = deque()


def init_request_sensor():
    print("Push request to sensor")
    if(len(list_request) <= 0):
        fetch_api()
    if(len(list_request) > 0):
        generate_request()

def pub_response():
    while True:
        if(len(response_queue) > 0):
            response = response_queue.pop()
            print(response)


def generate_request():
    # list_send = []
    for request in list_request:
        obj_request = {
            "id": request["id"],
            "requests": "",
            "address": request["address"]
        }
        address_sensor = request["address"].split(",")
        for label in request["labels"]:
            address_label = label["address"].split(",")
            item_request = []
            item_request.append(address_sensor[0])
            item_request.append(address_sensor[1])
            item_request.append(address_label[0])
            item_request.append(address_label[1])
            item_request.append(address_label[2])
            item_request.append(address_label[3])
            obj_request["requests"] = chkSum.generate_modbus_message(
                item_request)
            response_queue.append({"topic": "sensor_data", "value": sensor_connect.sendRequestToSensor(obj_request)})


def fetch_api():
    list_result = APIHandler.get_request()
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


def automation_trigger(message):
    obj = json.loads(message.value)
    obj["requests"] = chkSum.generate_modbus_message(obj["requests"])
    response_queue.append({"topic": "sensor_data", "value": sensor_connect.sendRequestToSensor(obj)})


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()


def ai_run():
    response_queue.append({"topic": "camera_data", "value": AI.start(cam, model)})

schedule.every(5).seconds.do(jobqueue.put, init_request_sensor)
schedule.every(5).seconds.do(jobqueue.put, ai_run)
schedule.every(1).minutes.do(jobqueue.put, fetch_api)

def start():
    try:
        sensor_connect.startProcesses()
        worker_thread_request = threading.Thread(target=worker_main)
        worker_thread_response = threading.Thread(target=pub_response)
        worker_thread_automation = threading.Thread(target=KafkaHandler.sub, args=("automation_data", automation_trigger))
        worker_thread_request.setDaemon(True)
        worker_thread_automation.setDaemon(True)
        worker_thread_response.setDaemon(True)
        
        worker_thread_request.start()
        worker_thread_automation.start()
        worker_thread_response.start()

        loop_forever = True
        while loop_forever:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                loop_forever = False
    except serial_util.SerialException as serial_exception:
        sentry_sdk.capture_exception(serial_exception)
        logging.exception(serial_exception)
    except Exception as general_exception:
        sentry_sdk.capture_exception(general_exception)
        logging.exception(general_exception)
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    start()
