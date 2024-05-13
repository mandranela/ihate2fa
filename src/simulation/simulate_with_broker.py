import asyncio
import logging

from gdepc.gateway import GDEPC

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    gdepc = GDEPC()
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
