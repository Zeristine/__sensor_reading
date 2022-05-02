import os
import time 
import json 
import random 
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from dotenv import load_dotenv

class KafkaHandler:

    def __init__(self):
        load_dotenv()
        self.server = os.getenv("KAFKA_BOOTSTRAP_SERVERS_LOCAL")
    
    # Messages will be serialized as JSON 
    def serializer(message):
        return json.dumps(message).encode('utf-8')

    # Callback event after message pub
    def callback(err, msg):
        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            print("Message produced: %s" % (str(msg)))
    
    def _pub(self, topic, mess):
        producer = KafkaProducer(
            bootstrap_servers = self.server,
            # value_serializer = self.serializer,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type = 'gzip'
        )
        result = producer.send(topic, mess)
        return result
        # producer.poll(5)
        
    def _sub(self, topic):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers = self.server,
        )
        for message in consumer:
            print(message.value)