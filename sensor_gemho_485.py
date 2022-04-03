print("************* GEMHO Sensor 485 *************")
import serial.tools.list_ports
import time
from server_api import APIHandler, api_handler
from kafka_connect import KafkaHandler

gemho_002_temperature   = [0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A]
gemho_002_humidity      = [0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA]
old_gemho_002_co2       = [0x02, 0x03, 0x00, 0x04, 0x00, 0x01, 0xC5, 0xF8]
gemho_002_co2           = [0x01, 0x03, 0x00, 0x04, 0x00, 0x01, 0xC5, 0xF8]
gemho_002_light         = [0x01, 0x03, 0x00, 0x02, 0x00, 0x02, 0x65, 0xCB]
messages = [gemho_002_temperature,
            gemho_002_humidity,
            gemho_002_light,
            gemho_002_co2
            ]
labels = ["Temperature", "Humidity", "Light", "CO2"]


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
        # print(len(data_array))
        # print(data_array)
        label = labels[pos]
        if label == "Temperature" or label == "Humidity":
            value = (data_array[3]*256 + data_array[4])/10
            print(label + ":",  value)
        elif label == "Light":
            value = (data_array[6]*256 + data_array[7])/10
            print(label + ":",  value)
            

def fetchStat(pos):
    ser.write(serial.to_bytes(messages[pos]))
    time.sleep(1)
    readSerial(pos)

# ************************************************************************
# Start here
# ************************************************************************
port, comPortStr = getPort()
ser = serial.Serial( port=comPortStr, baudrate=9600)
api_handler = APIHandler()
api_handler._create_device({
    'device' : port.device,
    'name' : port.name,
    'description' : port.description,
    'hwid' : port.hwid,
    'vid' : port.vid,
    'pid' : port.pid,
    'product' : port.product,
    'location' : port.location
})
n = 1;
isRunning = True
while isRunning:
    
    print("********************************************")
    print("Take ", n)
    fetchStat(0)
    fetchStat(1)
    fetchStat(2)
    n += 1

    if n == 2:
        isRunning = False
    time.sleep(5)