import json
import asyncio

from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_1
from simulation.sensors import SensorsBrokerSimulation
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def test_publish_coro():
    C = MQTTClient()
    await C.connect("mqtt://127.0.0.1:8081/")
    messages = []
    for message in SensorsBrokerSimulation.iter_test_message():
        messages.append(message)
        if len(messages) >= 10:
            logger.debug("Publish message from sensor!")

            try:
                encoded_messages = json.dumps(messages).encode()
                await C.publish("my-tcp-1", encoded_messages, qos=QOS_1, ack_timeout=10)
                await asyncio.sleep(1)
                messages = []
            except Exception as e:
                logger.exception("Fail to publish message from sensor!", exc_info=e)
