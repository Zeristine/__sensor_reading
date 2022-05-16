from pickle import TRUE
import time
import threading
import schedule
import queue
import crc_modbus_16_calculation as chkSum
from server_api.api_handler import APIHandler
from kafka_connect import KafkaHandler
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
            "requests" : []
        }
        address = request["address"].split(",")
        for label in request["labels"]:
            address_label = label["address"].split(",")
            item_request = []
            item_request.append(address[0])
            item_request.append(address[1])
            item_request.append(address_label[0])
            item_request.append(address_label[1])
            item_request.append("0x00")

            
            # high_byte, low_byte = chkSum.crc_modbus_calculate(item_request)
            # item_request.append(hex(low_byte))
            # item_request.append(hex(low_byte))
            obj_request["requests"].append(item_request)
        list_send.append(obj_request)  
    print(list_send)
        
def pub_response(response):
    print("Pub response to Kafka")
    instanceKafka = KafkaHandler()
    instanceKafka._pub("sensor_data",response)

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
schedule.every(1).minutes.do(jobqueue.put, fetch_api)

worker_thread = threading.Thread(target=worker_main)
worker_thread.start()

i = 0
while 1:
    schedule.run_pending()
    time.sleep(1)
    i = i + 1

