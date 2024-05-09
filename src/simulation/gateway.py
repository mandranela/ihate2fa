from asyncio import Queue
import hashlib
from logging import Logger
from random import randint, random
from typing import Dict, List, Optional
from packaging.main import KnapSack, PackageMessage, KnapSackWithStructId, KnapSackJson
import brotli
from google.protobuf.message import Message
from google.protobuf import descriptor_pb2
from settings import compression_decompression
import dateparser
import multiprocessing as mp
import asyncio
from multiprocessing.pool import Pool


class GDEPCSimulation:

    input_queue: Queue[dict]
    result_queue: Queue[Message]
    not_fully_packed: Queue[Message]

    descriptors_cache: Dict[str, descriptor_pb2.FileDescriptorSet] = {}

    def __init__(
        self,
        queue,
        logger: Logger,
        compression: str,
        include_descriptors=True,
        json_structure=False,
    ):
        self.input_queue = queue
        self.result_queue = Queue(maxsize=10)
        self.not_fully_packed = Queue(maxsize=5)
        self.include_descriptors = include_descriptors
        if json_structure and not include_descriptors:
            self.knapsack = KnapSackJson()
        elif include_descriptors:
            self.knapsack = KnapSack()
        else:
            self.knapsack = KnapSackWithStructId()

        self.knapsack.compression = compression
        self.logger = logger
        self.compression = compression
        self.include_descriptors = include_descriptors

    def recompress_with_additional_data(self, data, additional_data):
        decompressed_data = compression_decompression[self.compression][
            "decompression"
        ](data)
        decompressed_data += additional_data
        return compression_decompression[self.compression]["compression"](
            decompressed_data
        )

    def pack_message(self, message):
        columns = list(message.keys())
        columns.sort()
        hash = hashlib.sha256(" ".join(columns).encode()).hexdigest()
        cached_descriptor = self.descriptors_cache.get(hash)
        if cached_descriptor:
            self.logger.debug("Got descriptor from cache")
            package_message = PackageMessage.generate(
                message, self.compression, cached_descriptor
            )
            package_message.struct_id = randint(1, 100000)
            return package_message

        package_message = PackageMessage.generate(message, self.compression)
        package_message.struct_id = randint(1, 100000)

        self.logger.debug("Generate descriptor for message and save in cache")
        self.descriptors_cache[hash] = package_message.descriptor
        return package_message

    async def add_messages_to_input_queue(self):
        while len(self.knapsack.messages) < self.knapsack.max_messages:
            message = await self.input_queue.get()
            package_message = self.pack_message(message)
            self.knapsack.add_message(package_message)

    async def pack(self, estimated: Optional[int] = None):
        return self.knapsack.knapsack(estimated)

    async def packing(self):
        while True:
            await self.add_messages_to_input_queue()

            if self.not_fully_packed.full():
                new_pack = False
                self.logger.debug("Repack not fully packed pack")
                packed = await self.not_fully_packed.get()
            elif len(self.knapsack.messages) > 0:
                new_pack = True

                self.logger.debug("Packing new pack")

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
                if self.result_queue.full():
                    await self.result_queue.join()
                self.logger.debug("Put pack in result queue")
                await self.result_queue.put(packed)
            else:
                self.logger.debug("Put pack in not_fully_packed queue")
                await self.not_fully_packed.put(packed)

    async def flush(self) -> List[Message]:
        self.logger.debug("Flushing")
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
        return flushed
