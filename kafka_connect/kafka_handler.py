import json
import os
import random
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer


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
            bootstrap_servers=self.server,
            # value_serializer = self.serializer,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip'
        )
        result = producer.send(topic, mess)
        return result
        # producer.poll(5)

    def _sub(self, topic, listener):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.server,
        )
        consumer.poll(timeout_ms=6000)
        for msg in consumer:
            # print("Entered the loop\nKey: ", msg.key, " Value:", msg.value)
            listener(msg)
