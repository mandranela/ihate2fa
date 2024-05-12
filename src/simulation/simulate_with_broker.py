import asyncio
from simulation.broker import broker_coro
from simulation.publisher import test_publish_coro
from gdepc.gateway import GDEPC
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    broker = await broker_coro()
    gdepc = GDEPC("brotli", include_descriptors=False, json_structure=True)

    # стартуем брокер
    asyncio.create_task(broker.start())
    await asyncio.sleep(1)

    # стартуем отправку сообщений с сенсоров
    asyncio.create_task(test_publish_coro())

    # перекладываем в очередь на упаковку
    asyncio.create_task(gdepc.mqtt_2_queue("mqtt://127.0.0.1:8081/", "my-tcp-1"))

    # запускаем упаковку
    try:
        async for message in gdepc.packing():
            logger.debug(f"Message packed! Size {message.ByteSize() = }")
    finally:
        messages = await gdepc.flush()
        print(len(messages))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
