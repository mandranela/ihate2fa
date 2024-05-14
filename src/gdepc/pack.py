import hashlib
import json
import time
from typing import Callable, Dict, List
import pandas as pd
from google.protobuf import message_factory
from google.protobuf.message import Message
from google.protobuf import descriptor_pb2
from parse import get_proto_message_with_class
from gdepc.proto import package_compressed_pb2
from gdepc.proto import package_compressed_no_descriptors_pb2
from ortools.algorithms.python import knapsack_solver
from google.protobuf.json_format import MessageToDict
import logging
import os
import subprocess
import uuid
from gdepc.settings import XTOPROTO_PATH, GENERATED_PATH, compression_decompression, compression_dict
import base64
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_message_class(descriptor_set: descriptor_pb2.FileDescriptorSet) -> Message:
    """
    получаем класс сообщения из дескриптора
    """
    message_classes = message_factory.GetMessages(descriptor_set.file)
    return message_classes["mypackage.MyMessage"]

class Packaging:
    # кеш дескрипторов
    descriptors_cache: Dict[str, descriptor_pb2.FileDescriptorSet] = {}

    def pack_message(self, message: dict):
        """
        упаковываем сообщение с сенсора в объект
        """
        columns = list(message.keys())
        columns.sort()
        hash = hashlib.sha256(" ".join(columns).encode()).hexdigest()
        cached_descriptor = self.descriptors_cache.get(hash)
        if cached_descriptor:
            package_message = PackageMessage.generate(
                message, cached_descriptor
            )
            return package_message

        package_message = PackageMessage.generate(message)

        logger.debug("Generate descriptor for message and save in cache")
        self.descriptors_cache[hash] = package_message.descriptor
        package_message.json_message = message
        return package_message
    

class PackageMessageData:

    dataset_name: str
    dataset_message_index: str
    compression: str

    compressed_proto_message: bytes
    compressed_json_message: bytes
    compressed_descriptor: bytes

    proto_compression_time: float
    json_compression_time: float
    descriptor_compression_time: float

    proto_message_size: int
    json_message_size: int
    descriptor_size: int

    compressed_proto_message_size: int
    compressed_json_message_size: int
    compressed_descriptor_message_size: int

    def columns(self):
        list(self.to_dict_analytic().keys())

    def to_dict_analytic(self):

        return {
            'dataset_name': self.dataset_name,
            'dataset_message_index': self.dataset_message_index,
            'compression': self.compression,
            'proto_compression_time': self.proto_compression_time,
            'json_compression_time': self.json_compression_time,
            'descriptor_compression_time': self.descriptor_compression_time,
            'proto_message_size': self.proto_message_size,
            'json_message_size': self.json_message_size,
            'descriptor_size': self.descriptor_size,
            'compressed_proto_message_size': self.compressed_proto_message_size,
            'compressed_json_message_size': self.compressed_json_message_size,
            'compressed_descriptor_message_size': self.compressed_descriptor_message_size,
        }



class PackageMessage:
    """
    Класс обертка над сообщениями
    """

    proto_message: Message
    json_message: Dict
    descriptor: descriptor_pb2.FileDescriptorSet

    total_size: int
    struct_id: str

    def __init__(
        self,
        descriptor: descriptor_pb2.FileDescriptorSet,
        message_proto: Message,
        message_json: Message,
    ) -> None:

        self.descriptor = descriptor

        self.proto_message = message_proto

        self.json_message = message_json


    def compress_huffman(self, compression: Callable):
        data = PackageMessageData()
        data.descriptor_size = self.descriptor.ByteSize()
        data.proto_message_size = self.proto_message.ByteSize()
        data.json_message_size = len(json.dumps(self.json_message).encode())

        t = time.process_time()
        proto_string = base64.b64encode(self.proto_message.SerializeToString()).decode()
        data.compressed_proto_message = compression(proto_string)
        data.compressed_proto_message_size = len(
            data.compressed_proto_message
        )
        data.proto_compression_time = time.process_time() - t

        t = time.process_time()
        data.compressed_json_message = compression(json.dumps(self.json_message))

        data.compressed_json_message_size = len(
            data.compressed_json_message
        )
        data.json_compression_time = time.process_time() - t

        t = time.process_time()
        descriptor_string = base64.b64encode(self.descriptor.SerializeToString()).decode()
        data.compressed_descriptor = compression(descriptor_string)
        data.compressed_descriptor_message_size = len(
                data.compressed_descriptor
        )
        data.descriptor_compression_time = time.process_time() - t
        return data
        

    @classmethod
    def generate(cls, message: dict, descriptor=None):
        """
        собираем сообщения из данных с дескриптором и сжатия
        """
        name = str(uuid.uuid1())

        df = pd.DataFrame(message, index=[0])
        subprocess.run(
            ["mkdir", "-p", f"{GENERATED_PATH}/generated"],
            stdout=subprocess.DEVNULL,
        )
        if not descriptor:
            df.to_csv(
                f"{GENERATED_PATH}/generated/{name}.csv",
                index=False,
            )
            subprocess.run(
                [
                    f"{XTOPROTO_PATH}",
                    "-csv",
                    f"{GENERATED_PATH}/generated/{name}.csv",
                    "-default_workspace",
                    GENERATED_PATH,
                ],
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    "mv",
                    f"{GENERATED_PATH}/generated/example.proto",
                    f"{GENERATED_PATH}/generated/{name}.proto",
                ]
            )

            subprocess.run(
                [
                    "protoc",
                    f"-I={GENERATED_PATH}/generated",
                    f"--python_out={GENERATED_PATH}/generated",
                    "--include_imports",
                    f"--descriptor_set_out={GENERATED_PATH}/generated/{name}.dsc",
                    f"{GENERATED_PATH}/generated/{name}.proto",
                ]
            )

            DSCR_PATH = f"{GENERATED_PATH}/generated/{name}.dsc"
            with open(DSCR_PATH, "rb") as file:
                descriptor = descriptor_pb2.FileDescriptorSet.FromString(file.read())

            subprocess.run(
                [
                    "rm",
                    DSCR_PATH,
                    f"{GENERATED_PATH}/generated/{name}.proto",
                    f"{GENERATED_PATH}/generated/{name}.csv",
                    f"{GENERATED_PATH}/generated/{name.replace('-', '_')}_pb2.py",
                ]
            )
        message_class = get_message_class(descriptor)
        message_proto = get_proto_message_with_class(df.iloc[0], message_class)
        return cls(descriptor, message_proto, message)


class KnapSack:
    """
    Класс для упаковки по алгоритму рюкзака с дескрипторами
    """

    max_messages = 64
    # 360, 1960
    max_container = 1960
    messages: List[PackageMessage] = []
    priority: List[int] = []
    compression: str = "no_compression"

    def add_messages(self, messages: List[PackageMessage]):
        """
        добавляем сообщение в алгоритм
        """
        for message in messages:
            self.add_message(message)

    def add_message(self, message: PackageMessage):
        """
        добавляем сообщения в алгоритм
        """
        self.messages.append(message)
        self.priority.append(1)

    def pack_messages(self, indexes: List[int]):
        """
        упаковываем сообщения в контейнер
        """
        packed_messages: List[PackageMessage] = []
        for index in indexes:
            packed_messages.append(self.messages[index])
        self_describing_compressed: Message = (
            package_compressed_pb2.SelfDescribingCompressedMessage()
        )
        for message in packed_messages:
            self_describing_compressed.descriptor_set += compression_decompression[
                message.compression
            ]["compression"](message.descriptor.SerializeToString())
            self_describing_compressed.descriptor_sizes.append(
                len(
                    compression_decompression[message.compression]["compression"](
                        message.descriptor.SerializeToString()
                    )
                )
            )
            self_describing_compressed.message += compression_decompression[
                message.compression
            ]["compression"](message.proto_message.SerializeToString())
            self_describing_compressed.message_sizes.append(
                len(
                    compression_decompression[message.compression]["compression"](
                        message.proto_message.SerializeToString()
                    )
                )
            )

        return self_describing_compressed

    def knapsack(self, max_container=None):
        """
        упаковываем в контейнер
        """
        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.SolverType.KNAPSACK_64ITEMS_SOLVER,
            "KnapsackExample",
        )
        weights = [
            [message.total_size for message in self.messages],
        ]
        capacities = [max_container]
        if max_container is None:
            capacities = [self.max_container]
        logger.debug("Init solver")
        solver.init(self.priority, weights, capacities)
        logger.debug("Try to solve")
        computed_value = solver.solve()
        packed_items = []
        packed_weights = []
        total_weight = 0
        for i in range(len(self.priority)):
            if solver.best_solution_contains(i):
                packed_items.append(i)
                packed_weights.append(weights[0][i])
                total_weight += weights[0][i]
        if not packed_items:
            return None
        logger.debug("Pack items in container")

        result = self.pack_messages(packed_items)
        self.messages = [
            message
            for index, message in enumerate(self.messages)
            if index not in packed_items
        ]
        self.priority = [
            priority + 1
            for index, priority in enumerate(self.priority)
            if index not in packed_items
        ]
        return result


class KnapSackJson(KnapSack):
    """
    упаковываем в контейнер
    """

    max_messages = 64

    def add_message(self, message: PackageMessage):
        # only message
        message_data_raw: str = json.dumps(message.json_message)
        message_data_raw_compressed: bytes = compression_decompression[
            message.compression
        ]["compression"](message_data_raw.encode())
        message.compressed_proto_message_size = len(message_data_raw_compressed)
        message.total_size = len(message_data_raw_compressed) + 28
        self.messages.append(message)
        self.priority.append(1)

    def pack_messages(self, indexes: List[int]):
        packed_messages: List[PackageMessage] = []
        for index in indexes:
            packed_messages.append(self.messages[index])

        compressed_message: Message = (
            package_compressed_no_descriptors_pb2.CompressedMessage()
        )

        for message in packed_messages:
            message_data_raw: str = json.dumps(message.json_message)
            compressed_data = compression_decompression[message.compression][
                "compression"
            ](message_data_raw.encode())
            compressed_message.message += compressed_data
            compressed_message.message_sizes.append(len(compressed_data))

        return compressed_message


class KnapSackWithStructId(KnapSack):
    max_messages = 64

    def add_message(self, message: PackageMessage):
        # only message
        message.total_size -= message.descriptor_size
        self.messages.append(message)
        self.priority.append(1)

    def pack_messages(self, indexes: List[int]):
        packed_messages: List[PackageMessage] = []
        for index in indexes:
            packed_messages.append(self.messages[index])

        compressed_message: Message = (
            package_compressed_no_descriptors_pb2.CompressedMessage()
        )

        for message in packed_messages:
            compressed_message.message += compression_decompression[
                message.compression
            ]["compression"](message.proto_message.SerializeToString())
            compressed_message.message_sizes.append(
                len(
                    compression_decompression[message.compression]["compression"](
                        message.proto_message.SerializeToString()
                    )
                )
            )
            compressed_message.struct_id.append(message.struct_id)
        return compressed_message




class CompressionData:
    proto_bytes: bytes
    json_bytes: bytes
    descriptor_bytes: bytes
    

def compress_bytes(message: CompressionData, compression_name: str, dataset_name, index):
    data = PackageMessageData()
    data.descriptor_size = len(message.descriptor_bytes)
    data.proto_message_size = len(message.proto_bytes)
    data.json_message_size = len(message.json_bytes)
    data.compression = compression_name
    data.dataset_name = dataset_name
    data.dataset_message_index = index
    
    compression = compression_dict[compression_name]


    t = time.process_time()
    data.compressed_proto_message = bytes(compression(message.proto_bytes))
    data.compressed_proto_message_size = len(
        data.compressed_proto_message
    )
    data.proto_compression_time = time.process_time() - t

    t = time.process_time()
    data.compressed_json_message = bytes(compression(message.json_bytes))
    data.compressed_json_message_size = len(
        data.compressed_json_message
    )
    data.json_compression_time = time.process_time() - t

    t = time.process_time()
    data.compressed_descriptor = bytes(compression(
            message.descriptor_bytes
        ))

    data.compressed_descriptor_message_size = len(
        data.compressed_descriptor
    )
    data.descriptor_compression_time = time.process_time() - t
    return data
