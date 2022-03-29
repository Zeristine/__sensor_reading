print("************* GEMHO Sensor 485 *************")
import serial.tools.list_ports
import time
from server_api import APIHandler
from kafka_connect import KafkaHandler

gemho_002_temperature   = [0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A]
gemho_002_humidity      = [0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA]
old_gemho_002_co2       = [0x02, 0x03, 0x00, 0x04, 0x00, 0x01, 0xC5, 0xF8]
gemho_002_co2           = [0x01, 0x03, 0x00, 0x04, 0x00, 0x01, 0xC5, 0xF8]
gemho_002_light         = [0x01, 0x03, 0x00, 0x02, 0x00, 0x02, 0x65, 0xCB]
messages = [gemho_002_temperature,
            gemho_002_humidity,
            gemho_002_co2,
            gemho_002_light]
labels = ["Temperature", "Humidity", "CO2", "Light"]


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    # print(N)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        # print(port)
        if "USB" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    # return "COM23"
    print(commPort)
    return commPort

ser = serial.Serial( port=getPort(), baudrate=9600)

def readSerial(pos):
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        out = ser.read(bytesToRead)
        # print("Received:", out)
        data_array = [b for b in out]
        # print(len(data_array))
        # print(data_array)
        label = labels[pos]
        if label is "Temperature" or label is "Humidity":
            value = (data_array[3]*256 + data_array[4])/10
            print(label + ":",  value)
        elif label is "Light":
            value = (data_array[6]*256 + data_array[7])/10
            print(label + ":",  value)
            

def fetchStat(pos):
    ser.write(serial.to_bytes(messages[pos]))
    time.sleep(1)
    readSerial(pos)

n = 1;
while True:
    
    # length = 7
    # ser.write(serial.to_bytes(gemho_002_temperature))
    # time.sleep(1)
    # readSerial()
    # fetchStat(0)
    
    # length = 7
    # ser.write(serial.to_bytes(gemho_002_humidity))
    # time.sleep(1)
    # readSerial()
    # fetchStat(1)
    
    print("********************************************")
    print("Take ", n)
    fetchStat(0)
    fetchStat(1)
    # fetchStat(2)
    fetchStat(3)
    n += 1

    time.sleep(5)