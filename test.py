import kafka
from kafka_connect import KafkaHandler

kafka_instance = KafkaHandler()
kafka_instance._sub("sensor_data")