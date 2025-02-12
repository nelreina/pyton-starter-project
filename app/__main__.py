from dotenv import load_dotenv
from os import environ
import sys
import os
import logging
import signal
from redisstream import RedisStreamConsumer
from redis_client import RedisClient
from redis import Redis
import platform
import schedule
import time
import threading

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(message)s')


stream_key = environ.get("STREAM")
service_name = environ.get("SERVICE_NAME")
events = environ.get("STREAM_EVENTS", "NO_EVENTS").split(",")
consumer = platform.node()

def connect_to_redis():
    hostname = environ.get("REDIS_HOST", "localhost")
    port = environ.get("REDIS_PORT", 6379)
    password = environ.get("REDIS_PW")

    r = Redis(hostname, port, password=password,
              retry_on_timeout=True, client_name=service_name)
    return r


def callback(conn, id, event, aggregateId, payload, ack):
    logging.info(f"Event: {event} / {aggregateId}")
def terminate(signal, frame):
    logging.info("Terminating...")
    # Set termination flag
    ScheduleThread.stop_flag = True
    sys.exit(0)

def schedule_job(redis_client):
    logging.info("### Running job...")
    redis_client.addToStream(stream_key, "TEST", "TEST", {"message": "TEST"})

class ScheduleThread(threading.Thread):
    stop_flag = False  # Class variable to control termination

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        start_schedule()

def start_schedule():
    logging.info("Starting schedule...")
    connection = connect_to_redis()
    redis_client = RedisClient(connection, service_name)
    schedule.every(5).seconds.do(schedule_job, redis_client)
    while not ScheduleThread.stop_flag:  # Check termination flag
        schedule.run_pending()
        time.sleep(1)
    logging.info("Schedule thread stopping...")


def main():
    try:
        logging.info(f"running {service_name} ...")

        load_dotenv()
        connection = connect_to_redis()
        stream = RedisStreamConsumer(
            connection, stream_key, service_name, events)

        # Store threads to manage them during shutdown
        global callback_thread
        callback_thread = threading.Thread(target=stream.listen, args=(callback, "0"))
        callback_thread.start()
        
        global scheduler_thread
        scheduler_thread = ScheduleThread()

    except Exception as e:
        logging.info(f"{e}")
        sys.exit(0)


if __name__ == "__main__":
    try:
        # Register signal handler before starting threads
        signal.signal(signal.SIGTERM, terminate)
        signal.signal(signal.SIGINT, terminate)
        main()

    except KeyboardInterrupt:
        logging.info('Application is shutting down!')
        ScheduleThread.stop_flag = True  # Set termination flag
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
