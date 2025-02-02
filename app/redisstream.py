import json
import platform
import logging
from datetime import datetime


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class RedisStreamConsumer():
    """docstring for RedisStreamConsumer"""

    def __init__(self, conn, stream_key, group_name,  events):
        super(RedisStreamConsumer, self).__init__()
        self.conn = conn
        self.stream_key = stream_key
        self.group_name = group_name
        self.consumer = platform.node()
        self.events = events

    def _createOrJoinGroup(self, startID):
        try:
            self.conn.xgroup_create(
                self.stream_key, self.group_name, startID, mkstream=True)
            logging.info(
                f"Group '{self.group_name}' is created for stream '{self.stream_key}'!")
            return True
        except Exception as e:
            err_message = "{}".format(e)
            if "Group name already exists" in err_message:
                logging.info(
                    f"Group '{self.group_name}' has joined stream '{self.stream_key}'!")
                return True
            else:
                logging.info(err_message + ": " + self.group_name)
                return False

    def _registerConsumer(self):
        try:
            self.conn.xgroup_createconsumer(
                self.stream_key, self.group_name, self.consumer)
            logging.info(
                f"Consumer: {self.consumer} is registered in group {self.group_name}!")
            return True

        except Exception as e:
            err_message = "{}".format(e)
            logging.info(err_message + ": " + self.consumer)
            return False

    def _get_data(self, message):
        id, data = message
        id = id.decode("utf-8")

        event = data.get(b"event")
        event = event.decode("utf-8")
        aggregateId = data.get(b"aggregateId")
        aggregateId = aggregateId.decode("utf-8")
        payload = data.get(b"payload")
        payload = json.loads(payload.decode("utf-8"))

        return id,  event, aggregateId, payload

    def ack(self, id):
        resp = self.conn.xack(self.stream_key, self.group_name, id)

    def addToStream(self, event,  aggregateId, payload):
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        stream_data = {
            b"event": event,
            b"aggregateId": aggregateId,
            b"timestamp": timestamp,
            b"payload": payload
        }
        self.conn.xadd(self.stream_key, stream_data)
        pass

    def listen(self, callback, startID="$"):
        cont = self._createOrJoinGroup(startID)
        if not cont:
            raise Exception("Create or Join Group Error! ")

        cont = self._registerConsumer()
        if not cont:
            raise Exception("Register Consumer Error! ")

        logging.info(f"Listening to message from '{self.stream_key}'...")
        last_id = ">"
        sleep_ms = 5000
        while True:
            try:
                resp = self.conn.xreadgroup(
                    self.group_name, self.consumer,
                    {self.stream_key: last_id}, count=1, block=sleep_ms
                )
                if resp:
                    message = resp[0][1][0]
                    id, event, aggregateId,  payload = self._get_data(message)

                    if event in self.events:
                        callback(self.conn, id, event,
                                 aggregateId,  payload, self.ack, self.addToStream)
                    else:
                        # Auto Ack events that is not for this service
                        self.ack(id)

            except ConnectionError as e:
                logging.info("ERROR REDIS CONNECTION: {}".format(e))

