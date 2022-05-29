print("************* GEMHO Sensor 485 *************")
import serial.tools.list_ports
import time
from server_api import APIHandler, api_handler
from kafka_connect import KafkaHandler
from multiprocessing import Queue

# old_gemho_002_co2       = [0x02, 0x03, 0x00, 0x04, 0x00, 0x01, 0xC5, 0xF8]
# Gemho sending message
gemho_002_temperature   = [0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A]
gemho_002_humidity      = [0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA]
gemho_002_co2           = [0x01, 0x03, 0x00, 0x04, 0x00, 0x01, 0xC5, 0xF8]
gemho_002_light         = [0x01, 0x03, 0x00, 0x02, 0x00, 0x02, 0x65, 0xCB]
gemho_002_humid_mod = [1, 3, 0, 1, 0, 1, 213, 202]
# Soil Detection sending message
soil_detection_temperature   = [0x02, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x38]
soil_detection_humidity      = [0x02, 0x03, 0x00, 0x07, 0x00, 0x01, 0x35, 0xF8]
soil_detection_ec            = [0x02, 0x03, 0x00, 0x08, 0x00, 0x01, 0x05, 0xFB]
# Relay message
relay_rs485_on  = [15, 6, 0, 0, 0, 255, 200, 164]
relay_rs485_off = [15, 6, 0, 0, 0, 0, 136, 228]
messages = [gemho_002_temperature,
            gemho_002_humidity,
            gemho_002_light,
            gemho_002_co2,
            soil_detection_humidity,
            soil_detection_temperature,
            soil_detection_ec,
            relay_rs485_on,
            relay_rs485_off
            ]
labels = ["Temperature", "Humidity", "Light", "CO2", "Soil Humidity", "Soil Temperature",
          "Soil Electricity", "Relay On", "Relay Off"]


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    # print(N)
    commPort = "None"
    port = None
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        # print(port)
        if "USB" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    # return "COM23"
    print(commPort)
    return port, commPort

def readSerial(pos):
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        out = ser.read(bytesToRead)
        # print("Received:", out)
        data_array = [b for b in out]
        # print("Data Length", len(data_array))
        print("Data", data_array)
        label = labels[pos]
        value = 0
        match pos:
            case 0 | 1 | 7:
                value = (data_array[3]*256 + data_array[4])/10
            case 2:
                value = (data_array[6]*256 + data_array[7])/10
            case 4:
                value = (data_array[3]*256 + data_array[4])/100
            case 5:
                value = (data_array[3]*256 + data_array[4])/10
            case 6:
                value = (data_array[3]*256 + data_array[4])/10
            case 7 | 8:
                value = data_array
        print(label + ":",  value)        
            

def fetchStat(pos):
    print(messages[pos])
    ser.write(serial.to_bytes(messages[pos]))
    time.sleep(0.5)
    readSerial(pos)

def getSensorResponse(request):
    ser.write(serial.to_bytes(request))
    # time.sleep(1)
    bytesToRead = ser.inWaiting()
    value = 0
    label = request[1:3]
    if (bytesToRead > 0):
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        match len(data_array):
            case 6:
                value = (data_array[3]*256 + data_array[4])/10
            case 8:
                value = (data_array[6]*256 + data_array[7])/10
    return {'address':label, 'value':value}

def getMultipleSensorResponses(devices):
    result = []
    for device in devices:
        id = device.id
        responses = []
        for request in device.requests:
            responses.append(getSensorResponse(request=request))
        result.append({'id' : id, 'response' : responses})
    return result

# ************************************************************************
# Start here
# ************************************************************************
port, comPortStr = getPort()
ser = serial.Serial(
    port=comPortStr,
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
    write_timeout=1
    )
# api_handler = APIHandler()
# api_handler._get_devices()
# api_handler._create_device({
#     'device' : port.device,
#     'name' : port.name,
#     'description' : port.description,
#     'hwid' : port.hwid,
#     'vid' : port.vid,
#     'pid' : port.pid,
#     'product' : port.product,
#     'location' : port.location
# })

print("HWID: " + str(port.hwid) + ", vid: " + str(port.vid) + ", pid: " + str(port.pid))

n = 1
isRunning = True
while isRunning:
    
    print("********************************************")
    print("Take ", n)
    fetchStat(7)
    fetchStat(0)
    fetchStat(1)
    fetchStat(5)
    fetchStat(2)
    fetchStat(4)
    fetchStat(6)
    fetchStat(8)
    n += 1

    if n > 2:
        isRunning = False
    time.sleep(1)