import json
import platform
from datetime import datetime
from logger import logger


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
            logger.info(
                f"✨ Group '{self.group_name}' is created for stream '{self.stream_key}'!")
            return True
        except Exception as e:
            err_message = str(e)
            if "Group name already exists" in err_message:
                logger.info(
                    f"🔄 Group '{self.group_name}' has joined stream '{self.stream_key}'!")
                return True
            else:
                logger.error(f"❌ {err_message}: {self.group_name}")
                return False

    def _registerConsumer(self):
        try:
            self.conn.xgroup_createconsumer(
                self.stream_key, self.group_name, self.consumer)
            logger.info(
                f"✅ Consumer: {self.consumer} is registered in group {self.group_name}!")
            return True

        except Exception as e:
            err_message = str(e)
            logger.error(f"❌ {err_message}: {self.consumer}")
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

        logger.struct("Received message:", {
            "id": id,
            "event": event,
            "aggregateId": aggregateId,
            "payload": payload
        })

        return id, event, aggregateId, payload

    def ack(self, id):
        resp = self.conn.xack(self.stream_key, self.group_name, id)

    def listen(self, callback, startID="$"):
        cont = self._createOrJoinGroup(startID)
        if not cont:
            raise Exception("Create or Join Group Error!")

        cont = self._registerConsumer()
        if not cont:
            raise Exception("Register Consumer Error!")

        logger.info(f"👂 Listening to message from '{self.stream_key}'...")
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
                                 aggregateId,  payload, self.ack)
                    else:
                        # Auto Ack events that is not for this service
                        self.ack(id)

            except ConnectionError as e:
                logger.info("ERROR REDIS CONNECTION: {}".format(e))

