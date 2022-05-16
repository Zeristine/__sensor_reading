import kafka
from kafka_connect import KafkaHandler
instance = KafkaHandler()
instance._sub("camera_data")