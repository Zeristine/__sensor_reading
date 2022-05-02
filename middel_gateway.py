# import time
# from server_api import APIHandler, api_handler
# from kafka_connect import KafkaHandler

#region Sub topic schedule
# kafka = KafkaHandler()
# kafka._sub(topic = "sample")
#endregion

# def _push_kafka(response):
#     kafka = KafkaHandler()
#     return kafka._pub(topic = "sample")

#region Fetch data sever every 5seconds for get request sensor
# while True:
#     request = APIHandler._get_request()
#     print(request)
#     time.sleep(5)
#endregion

from pickle import TRUE
import time
import threading
import schedule
import queue
import crc_modbus_16_calculation as chkSum
from server_api.api_handler import APIHandler

list_request = []
def push_sensor_request():
    print("Push request to sensor")
    if(len(list_request) <= 0):
        fetch_api()
    if(len(list_request) > 0):
        #push to sensor
        # print(list_request)
        generate_request()

def generate_request():
    for request in list_request:
        requests = []
        print(request)
        address = request["address"].split(",")
        for label in request["labels"]:
            address_label = label["address"].split(",")
            item_request = []
            
            # item_request.append(hex(int(address[0], 16)))
            # item_request.append(hex(int(address[1], 16)))
            # item_request.append(hex(int(address_label[0], 16)))
            # item_request.append(hex(int(address_label[0], 16)))
            # item_request.append(hex(0x00))
            # item_request.append(hex(0x01))
            item_request.append(address[0])
            item_request.append(address[1])
            item_request.append(address_label[0])
            item_request.append(address_label[1])
            item_request.append(hex("0x00"))
            item_request.append("0x01")
            print(item_request)
            # high_byte, low_byte = chkSum.crc_modbus_calculate(item_request)
            # item_request.append(hex(high_byte))
            # item_request.append(hex(low_byte))
            
            # "[{0},{1},{2},{3},{4},{5},{6},{7}]".format()
            # tmp = "[{0},{1},{2},{3}]".format(request["address"], label["address"], "0x00,0x01", "0x00,0x01")
            # print(item_request)


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
    print(i)

