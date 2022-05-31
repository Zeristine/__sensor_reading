from multiprocessing import Manager, Process
import time


class Worker(Process):
    """
    Simple worker.
    """

    def __init__(self, name, in_queue, out_queue):
        super(Worker, self).__init__()
        self.name = name
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            # grab work; do something to it (+1); then put the result on the output queue
            work = self.in_queue.get()
            print("{} got {}".format(self.name, work))
            work += 1

            # sleep to allow the other workers a chance (b/c the work action is too simple)
            time.sleep(1)

            # put the transformed work on the queue
            print("{} puts {}".format(self.name, work))
            self.out_queue.put(work)


if __name__ == "__main__":
    # construct the queues
    manager = Manager()
    inq = manager.Queue()
    outq = manager.Queue()

    # construct the workers
    workers = [Worker(str(name), inq, outq) for name in range(3)]
    for worker in workers:
        worker.start()

    # add data to the queue for processing
    work_len = 10
    for x in range(work_len):
        inq.put(x)

    while outq.qsize() != work_len:
        # waiting for workers to finish
        print("Waiting for workers. Out queue size {}".format(outq.qsize()))
        time.sleep(1)

    # clean up
    for worker in workers:
        worker.terminate()

    # print the outputs
    while not outq.empty():
        print(outq.get())

from kafka import KafkaConsumer
import threading

BOOTSTRAP_SERVERS = ['localhost:9092']

def register_kafka_listener(topic, listener):
# Poll kafka
    def poll():
        # Initialize consumer Instance
        consumer = KafkaConsumer(topic, bootstrap_servers=BOOTSTRAP_SERVERS)

        print("About to start polling for topic:", topic)
        consumer.poll(timeout_ms=6000)
        print("Started Polling for topic:", topic)
        for msg in consumer:
            print("Entered the loop\nKey: ",msg.key," Value:", msg.value)
            kafka_listener(msg)
    print("About to register listener to topic:", topic)
    t1 = threading.Thread(target=poll)
    t1.start()
    print("started a background thread")

def kafka_listener(data):
    print("Image Ratings:\n", data.value.decode("utf-8"))
