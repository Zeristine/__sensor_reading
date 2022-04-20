import time
from server_api import APIHandler, api_handler
from kafka_connect import KafkaHandler

#region Sub topic schedule
kafka = KafkaHandler()
kafka._sub(topic = "sample")
#endregion

#region Fetch data sever every 5seconds for get request sensor
while True:
    request = APIHandler._get_request()
    print(request)
    time.sleep(5)
#endregion