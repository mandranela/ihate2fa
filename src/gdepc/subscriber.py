import asyncio
import json
import logging
from typing import Dict

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_1


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def subscriber_coro(url, topic):
    C = MQTTClient()
    await C.connect(url)
    await C.subscribe(
        [
            (topic, QOS_1),
        ]
    )
    try:
        while True:
            try:
                message = await C.deliver_message(timeout=10)
                logger.debug("Got message from sensor")
                packet = message.publish_packet
                json_message: Dict = json.loads(packet.payload.data)
                yield json_message
            except Exception:
                await C.unsubscribe(
                    [
                        topic,
                    ]
                )
                await C.subscribe(
                    [
                        (topic, QOS_1),
                    ]
                )
                await C.reconnect()
                logger.error("Wrong json format in message from sensor!")

    except ClientException as ce:
        logger.error("Client exception: %s" % ce)
    finally:
        await C.unsubscribe(
            [
                topic,
            ]
        )
        await C.disconnect()
