import json
from typing import Dict, List
import pandas as pd
from google.protobuf import message_factory
from google.protobuf.message import Message
from google.protobuf import descriptor_pb2
from parse import get_proto_message_with_class
from settings import compression_decompression
from packaging.proto import package_compressed_pb2
from packaging.proto import package_compressed_no_descriptors_pb2
from ortools.algorithms.python import knapsack_solver
from google.protobuf.json_format import MessageToDict
import logging
import os
import subprocess
import uuid
from gdepc.settings import XTOPROTO_PATH, GENERATED_PATH

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_message_class(descriptor_set: descriptor_pb2.FileDescriptorSet) -> Message:
    message_classes = message_factory.GetMessages(descriptor_set.file)
    return message_classes["mypackage.MyMessage"]


def recompress_with_additional_data(data, additional_data, compression, decompression):
    decompressed_data = decompression(data)
    decompressed_data += additional_data
    return compression(decompressed_data)


class PackageMessage:
    descriptor: descriptor_pb2.FileDescriptorSet
    message: Message
    message_data: Dict
    descriptor_size: int
    message_size: int
    total_size: int
    struct_id: str

    compression: str = "no_compression"

    def __init__(
        self,
        descriptor: descriptor_pb2.FileDescriptorSet,
        message: Message,
        compression: str,
    ) -> None:
        self.descriptor = descriptor
        self.message = message
        self.message_data = MessageToDict(message)
        self.compression = compression
        self.descriptor_size = len(
            compression_decompression[self.compression]["compression"](
                descriptor.SerializeToString()
            )
        )
        self.message_size = len(
            compression_decompression[self.compression]["compression"](
                message.SerializeToString()
            )
        )
        self.total_size = self.descriptor_size + self.message_size

    @classmethod
    def generate(cls, message: dict, compression: str, descriptor=None):
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
        message = get_proto_message_with_class(df.iloc[0], message_class)
        return cls(descriptor, message, compression)


class KnapSack:
    max_messages = 64
    # 360, 1960
    max_container = 1960
    messages: List[PackageMessage] = []
    priority: List[int] = []
    compression: str = "no_compression"

    def add_messages(self, messages: List[PackageMessage]):
        for message in messages:
            self.add_message(message)

    def add_message(self, message: PackageMessage):
        self.messages.append(message)
        self.priority.append(1)

    def pack_messages(self, indexes: List[int]):
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
            ]["compression"](message.message.SerializeToString())
            self_describing_compressed.message_sizes.append(
                len(
                    compression_decompression[message.compression]["compression"](
                        message.message.SerializeToString()
                    )
                )
            )

        return self_describing_compressed

    def knapsack(self, max_container=None):

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
    max_messages = 64

    def add_message(self, message: PackageMessage):
        # only message
        message_data_raw: str = json.dumps(message.message_data)
        message_data_raw_compressed: bytes = compression_decompression[
            message.compression
        ]["compression"](message_data_raw.encode())
        message.message_size = len(message_data_raw_compressed)
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
            message_data_raw: str = json.dumps(message.message_data)
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
            ]["compression"](message.message.SerializeToString())
            compressed_message.message_sizes.append(
                len(
                    compression_decompression[message.compression]["compression"](
                        message.message.SerializeToString()
                    )
                )
            )
            compressed_message.struct_id.append(message.struct_id)
        return compressed_message
