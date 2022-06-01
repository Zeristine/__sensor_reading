import kafka
from kafka_connect import KafkaHandler
instance = KafkaHandler()
instance._sub("sensor_data")