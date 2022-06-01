import os
import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from dotenv import load_dotenv

load_dotenv()
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS_LOCAL")


# producer = KafkaProducer(
#     bootstrap_servers=['localhost:9092'],
#     value_serializer=serializer,
#     compression_type='gzip'
# )

def pub(topic, mess):
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            # value_serializer = self.serializer,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip'
        )
        result = producer.send(topic, mess)
        return result

def sub(topic, listener):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=BOOTSTRAP_SERVERS,
        )
        consumer.poll(timeout_ms=6000)
        for msg in consumer:
            # print("Entered the loop\nKey: ", msg.key, " Value:", msg.value)
            listener(msg)

def callback(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))
