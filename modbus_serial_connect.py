from multiprocessing import Queue, Process
import serial.tools.list_ports
import time
import middel_gateway
serial_model = None
request_queue = Queue()
response_queue = Queue()

dict_sensor = {}
# labels = ["Temperature", "Humidity", "Light", "CO2", "Soil Humidity", "Soil Temperature",
#           "Soil Electricity"]


def getAvailableComPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    port = None
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return port, commPort


def initSerialModel():
    global serial_model
    global request_queue
    global response_queue
    request_queue = Queue()
    response_queue = Queue()
    # if serial_model == None:
    _, comPortStr = getAvailableComPort()
    serial_model = serial.Serial(
        port=comPortStr,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
        write_timeout=1)


def getSensorResponse(queue):
    # global response_queue
    if queue.empty():
        if response_queue != None:
            response_queue.put({})
    else:
        request = queue.get()
        for request_message in request["requests"]:
            print(request_message)
            serial_model.write(serial.to_bytes(request_message))
            time.sleep(0.5)
            bytesToRead = serial_model.inWaiting()
            value = 0
            label = request_message[2:4]
            if (bytesToRead > 0):
                output = serial_model.read(bytesToRead)
                data_array = [data for data in output]
                match len(data_array):
                    case 7:
                        value = (data_array[3]*256 + data_array[4])/10
                    case 9:
                        value = (data_array[6]*256 + data_array[7])/10
            middel_gateway.pub_response(
                {'id': request["id"], 'address': label, 'value': value})
            response_queue.put(
                {'id': request["id"], 'address': label, 'value': value})
            # middel_gateway.pub_response({'label': labels[label[1]], 'address':label, 'value':value})
            # response_queue.put({'label': labels[label[1]], 'address': label, 'value': value})

# Processing Response


def sendResponseToMiddleGateWay(queue):
    print("Send queue response")
    response = queue.get()
    print(response)
    # Method của anh Lộc


def addRequestsToQueue(external_requests):
    # global request_queue
    print("Add queue")
    for request in external_requests:
        # dict_sensor[request["address"]] = request["id"]
        request_queue.put(request)
    getSensorResponse(request_queue)


def startProcesses():
    initSerialModel()
    # request_process = Process(target=getSensorResponse, args=(request_queue,))
    # request_process.start()

    # response_process = Process(
    #     target=sendResponseToMiddleGateWay, args=(response_queue,))
    # response_process.start()

    # request_queue.join()
    # response_queue.join()

#######################################################################################################
#######################################################################################################
#######################################################################################################

# request_process = Process(target=getSensorResponse, args=(request_queue,))
# response_process = Process(target=sendResponseToMiddleGateWay, args=(response_queue,))
# if __name__ ==  '__main__':
#     startProcesses()

# request_process.join()
# response_process.join()


if __name__ == "__main__":
    startProcesses()
