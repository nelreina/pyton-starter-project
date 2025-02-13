# import json
# import platform
from datetime import datetime
from logger import logger

class RedisClient:
    def __init__(self, conn, service_name):
        self.conn = conn
        self.service_name = service_name

    def addToStream(self, stream_key, event, aggregateId, payload):
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # payload = json.dumps(payload)

        stream_data = {
            b"event": event,
            b"aggregateId": aggregateId,
            b"timestamp": timestamp,
            b"payload": payload,
            b"serviceName": self.service_name
        }
        self.conn.xadd(stream_key, stream_data)
        logger.debug(f"📤 Event {event}: {aggregateId}")
        pass

