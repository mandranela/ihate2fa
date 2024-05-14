from asyncio import Queue
import hashlib
from typing import Dict, List, Optional
from gdepc.pack import KnapSack, PackageMessage, KnapSackWithStructId, KnapSackJson
from google.protobuf.message import Message
from google.protobuf import descriptor_pb2
from gdepc.settings import compression_decompression
import asyncio
import logging
from gdepc.subscriber import subscriber_coro

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GDEPC:

    max_messages = 64  # максимальное число сообщений для упаковки
    input_queue: Queue[dict]  # очередь сообщений с сенсоров
    result_queue: Queue[Message]  # очередь из контейнеров
    not_fully_packed: Queue[Message]  # служебная очередь
    running = False

    descriptors_cache: Dict[str, descriptor_pb2.FileDescriptorSet] = (
        {}
    )  # кеш дескрипторов, используется с контейнерами с дескрипторами

    def __init__(
        self,
        compression: str = "brotli",
        include_descriptors=False,
        json_structure=True,
    ):
        """
        метод для создания GDEPC
        """
        self.input_queue = asyncio.Queue(maxsize=self.max_messages)
        self.result_queue = Queue()
        self.not_fully_packed = Queue(maxsize=5)
        self.include_descriptors = include_descriptors
        if json_structure and not include_descriptors:
            self.knapsack = KnapSackJson()
        elif include_descriptors:
            self.knapsack = KnapSack()
        else:
            self.knapsack = KnapSackWithStructId()

        self.knapsack.compression = compression
        self.compression = compression
        self.include_descriptors = include_descriptors

    def recompress_with_additional_data(self, data, additional_data):
        """
        добавляем в контейнер дополнительные данные
        """
        decompressed_data = compression_decompression[self.compression][
            "decompression"
        ](data)
        decompressed_data += additional_data
        return compression_decompression[self.compression]["compression"](
            decompressed_data
        )

    def pack_message(self, message):
        """
        упаковываем сообщение с сенсора в объект
        """
        columns = list(message.keys())
        columns.sort()
        hash = hashlib.sha256(" ".join(columns).encode()).hexdigest()
        cached_descriptor = self.descriptors_cache.get(hash)
        if cached_descriptor:
            package_message = PackageMessage.generate(
                message, self.compression, cached_descriptor
            )
            return package_message

        package_message = PackageMessage.generate(message, self.compression)

        logger.debug("Generate descriptor for message and save in cache")
        self.descriptors_cache[hash] = package_message.descriptor
        return package_message

    async def mqtt_2_queue(self, url, topic):
        """
        вычитывает из брокера и перекладывает в очередь сообщений
        """
        try:
            messages_num = 0
            while True:
                async for messages in subscriber_coro(url, topic):
                    logger.debug(f"Put messages {messages_num}")
                    messages_num += len(messages)
                    for message in messages:
                        await self.input_queue.put(message)
        except Exception:
            logger.exception("Fail to put message in input queue!")

    async def add_messages_to_input_queue(self):
        """
        добавляем сообщения из очереди сообщений в алгоритм упаковки пока не заполним
        """
        logger.debug("Add messages to queue")

        while len(self.knapsack.messages) < self.knapsack.max_messages:
            if not self.input_queue.empty():
                message = await asyncio.wait_for(self.input_queue.get(), timeout=1)
                package_message = self.pack_message(message)
                self.knapsack.add_message(package_message)
            else:
                logger.debug("Empty input queue!")
                await asyncio.sleep(1)

    async def pack(self, estimated: Optional[int] = None):
        """
        упаковываем в контейнер
        """
        return self.knapsack.knapsack(estimated)

    async def packing(self):
        """
        запускаем упаковку
        """
        while True:
            await self.add_messages_to_input_queue()

            if self.not_fully_packed.full():
                new_pack = False
                logger.debug("Repack not fully packed pack")
                packed = await self.not_fully_packed.get()
            elif len(self.knapsack.messages) > 0:
                new_pack = True

                logger.debug("Packing new pack")

                packed = await self.pack(None)
                if self.include_descriptors:
                    packed.descriptor_set = compression_decompression[self.compression][
                        "compression"
                    ](packed.descriptor_set)
                packed.message = compression_decompression[self.compression][
                    "compression"
                ](packed.message)

            estimated = self.knapsack.max_container - packed.ByteSize()

            if estimated >= 0 and len(self.knapsack.messages) > 0:
                await self.add_messages_to_input_queue()
                logger.debug("Packing second pack")

                second_packed = await self.pack(estimated)
            else:
                second_packed = None

            while second_packed:
                await self.add_messages_to_input_queue()
                if self.include_descriptors:
                    packed.descriptor_set = self.recompress_with_additional_data(
                        packed.descriptor_set, second_packed.descriptor_set
                    )
                    packed.descriptor_sizes.extend(second_packed.descriptor_sizes)
                else:
                    packed.struct_id.extend(second_packed.struct_id)
                packed.message = self.recompress_with_additional_data(
                    packed.message, second_packed.message
                )
                packed.message_sizes.extend(second_packed.message_sizes)
                estimated = self.knapsack.max_container - packed.ByteSize()
                if estimated >= 0 and len(self.knapsack.messages) > 0:
                    second_packed = await self.pack(estimated)
                else:
                    second_packed = None

            if (
                packed.ByteSize() / self.knapsack.max_container * 100 > 95
                or not new_pack
            ):
                yield packed
            else:
                logger.debug("Put pack in not_fully_packed queue")
                await self.not_fully_packed.put(packed)

    async def flush(self) -> List[Message]:
        """
        проталкиваем оставшиеся сообщения и контейнеры
        """
        logger.debug("Flushing")
        flushed = []
        while not self.not_fully_packed.empty():
            packed = await self.not_fully_packed.get()
            estimated = self.knapsack.max_container - packed.ByteSize()
            if estimated >= 0 and len(self.knapsack.messages) > 0:
                second_packed = self.knapsack.knapsack(estimated)
            else:
                second_packed = None

            while second_packed:
                if self.include_descriptors:
                    packed.descriptor_set = self.recompress_with_additional_data(
                        packed.descriptor_set, second_packed.descriptor_set
                    )
                    packed.descriptor_sizes.extend(second_packed.descriptor_sizes)
                else:
                    packed.struct_id.extend(second_packed.struct_id)
                packed.message = self.recompress_with_additional_data(
                    packed.message,
                    second_packed.message,
                    compression_decompression[self.compression]["compression"],
                    compression_decompression[self.compression]["decompression"],
                )
                packed.message_sizes.extend(second_packed.message_sizes)
                estimated = self.knapsack.max_container - packed.ByteSize()
                if estimated >= 0 and len(self.knapsack.messages) > 0:
                    second_packed = self.knapsack.knapsack(estimated)
                else:
                    second_packed = None
            flushed.append(packed)

        while not self.result_queue.empty():
            message = await self.result_queue.get()
            flushed.append(message)
        return flushed
