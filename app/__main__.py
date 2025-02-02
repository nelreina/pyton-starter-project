from dotenv import load_dotenv
from os import environ
import sys
import os
import logging
import signal
from redisstream import RedisStreamConsumer
from redis import Redis
import platform
import schedule
import time
import threading

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(message)s')


stream_key = environ.get("STREAM")
service_name = environ.get("SERVICE_NAME")
events = environ.get("STREAM_EVENTS").split(",")
consumer = platform.node()

def connect_to_redis():
    hostname = environ.get("REDIS_HOST", "localhost")
    port = environ.get("REDIS_PORT", 6379)
    password = environ.get("REDIS_PW")

    r = Redis(hostname, port, password=password,
              retry_on_timeout=True, client_name=service_name)
    return r


def callback(conn, id, event, aggregateId, payload, ack, addToStream):
    logging.info(f"Event: {event} / {aggregateId}")
    ack(id)

def terminate(signal, frame):
    logging.info("Terminating...")
    sys.exit(0)

def schedule_job():
    logging.info("### Running job...")

class ScheduleThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        start_schedule()

def start_schedule():
    logging.info("Starting schedule...")
    schedule.every(5).seconds.do(schedule_job)
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    try:
        logging.info(f"running {service_name} ...")

        load_dotenv()
        connection = connect_to_redis()
        stream = RedisStreamConsumer(
            connection, stream_key, service_name, events)

        callback_thread = threading.Thread(target=stream.listen, args=(callback, "0"))
        callback_thread.start()
        ScheduleThread()

    except Exception as e:
        logging.info(f"{e}")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
        signal.signal(signal.SIGTERM, terminate)

    except KeyboardInterrupt:
        logging.info('Application is shuting down!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
