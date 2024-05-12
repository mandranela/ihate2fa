import bz2
import gzip
import json
import lzma
from random import choice, seed
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
from google.protobuf import message_factory
from google.protobuf.message import Message
from google.protobuf import descriptor_pb2
from google.protobuf.any_pb2 import Any
from parse import get_proto_message_with_class
import brotli
from settings import datasets, test_structs_ids, compression_decompression
from packaging.proto import package_compressed_pb2
from packaging.proto import package_compressed_no_descriptors_pb2
import subprocess
from ortools.algorithms.python import knapsack_solver
import zlib
import brotli
from google.protobuf.json_format import MessageToDict
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


GENERATED_PATH = "/Users/vladislavkovazin/miem/gdepc/src"
XTOPROTO_PATH = "/Users/vladislavkovazin/miem/xtoproto/cmd/xtoproto"
PROTOC_RUN = f"protoc -I={GENERATED_PATH}/generated --python_out={GENERATED_PATH}/generated {GENERATED_PATH}/generated/example.proto"


SEED = 10
seed(SEED)
np.random.seed(SEED)


def get_df(name):
    df = pd.read_csv(f"/Users/vladislavkovazin/miem/gdepc/static/datasets/{name}.csv")
    df = df.replace(r"^\s*$", None, regex=True)
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    return df


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
        import os
        import subprocess
        import uuid

        df = pd.DataFrame(message, index=[0])

        if not descriptor:
            name = str(uuid.uuid1())
            df.to_csv(
                f"/Users/vladislavkovazin/miem/gdepc/src/generated/{name}.csv",
                index=False,
            )
            os.chdir("/Users/vladislavkovazin/miem/xtoproto")
            subprocess.run(
                [
                    "go",
                    "run",
                    f"{XTOPROTO_PATH}/xtoproto.go",
                    "-csv",
                    f"/Users/vladislavkovazin/miem/gdepc/src/generated/{name}.csv",
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

            os.chdir("/Users/vladislavkovazin/miem/gdepc/src/generated")
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

            DSCR_PATH = f"/Users/vladislavkovazin/miem/gdepc/src/generated/{name}.dsc"
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


class Packaging:
    descriptors: Dict[str, descriptor_pb2.FileDescriptorSet] = {}
    dfs: Dict[str, pd.DataFrame] = {}
    messages_num = 0

    def add_df(self, name):
        self.dfs[name] = get_df(name)
        self.messages_num += len(self.dfs[name])

    def generate(self, descriptors_only=False):
        import os
        import subprocess

        if not descriptors_only:
            os.chdir("/Users/vladislavkovazin/miem/xtoproto")
            for name in self.dfs:
                self.dfs[name][:10].to_csv(
                    f"/Users/vladislavkovazin/miem/gdepc/src/generated/{name}.csv",
                    index=False,
                )
                subprocess.run(
                    [
                        "go",
                        "run",
                        f"{XTOPROTO_PATH}/xtoproto.go",
                        "-csv",
                        f"/Users/vladislavkovazin/miem/gdepc/src/generated/{name}.csv",
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

            os.chdir("/Users/vladislavkovazin/miem/gdepc/src/generated")
            for name in self.dfs:
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

        for name in self.dfs:
            DSCR_PATH = f"/Users/vladislavkovazin/miem/gdepc/src/generated/{name}.dsc"
            with open(DSCR_PATH, "rb") as file:
                self.descriptors[name] = descriptor_pb2.FileDescriptorSet.FromString(
                    file.read()
                )

    def get_descriptor(self, name: str):
        return self.descriptors[name]

    def get_struct_id(self, name: str):
        return str(test_structs_ids[name])

    def get_messages_data(self, name, number: int):
        data = self.dfs[name]
        return data.iloc[:number]

    def get_message_data(self, name):
        data = self.dfs[name].sample()
        return data.iloc[0]

    def get_random_message(self):
        if self.messages_num <= 0:
            return None
        dataset_name = choice(list(self.dfs.keys()))
        while len(self.dfs[dataset_name]) == 0:
            dataset_name = choice(list(self.dfs.keys()))
        data = self.dfs[dataset_name].sample(random_state=SEED)
        descriptor = self.descriptors[dataset_name]
        message_class = get_message_class(descriptor)
        self.dfs[dataset_name].drop(data.index, inplace=True)
        message = get_proto_message_with_class(data.iloc[0], message_class)
        self.messages_num -= 1
        message = PackageMessage(descriptor, message)
        message.struct_id = self.get_struct_id(dataset_name)
        return message


def get_message_class(descriptor_set: descriptor_pb2.FileDescriptorSet) -> Message:
    message_classes = message_factory.GetMessages(descriptor_set.file)
    return message_classes["mypackage.MyMessage"]


def recompress_with_additional_data(data, additional_data, compression, decompression):
    decompressed_data = decompression(data)
    decompressed_data += additional_data
    return compression(decompressed_data)


def combine_self_described_message(alg: str):
    global compression_algorithm, decompression_algorithm
    if alg == "brotli":
        compression_algorithm = brotli.compress
        decompression_algorithm = brotli.decompress
    if alg == "lzma":
        compression_algorithm = lzma.compress
        decompression_algorithm = lzma.decompress
    if alg == "gzip":
        compression_algorithm = gzip.compress
        decompression_algorithm = gzip.decompress
    data = []
    packaging = Packaging()
    knapsack = KnapSack()
    knapsack.compression = alg if alg else "no_compression"
    packages_counter = 0
    for dataset_name in datasets:
        packaging.add_df(dataset_name)

    packaging.generate(descriptors_only=True)

    for _ in range(knapsack.max_messages):
        message = packaging.get_random_message()
        if message:
            knapsack.add_message(message)

    while packages_counter < 500:

        if len(knapsack.messages) < knapsack.max_messages:
            for _ in range(knapsack.max_messages - len(knapsack.messages)):
                message = packaging.get_random_message()
                if message:
                    knapsack.add_message(message)

        packed = knapsack.knapsack()
        packed.descriptor_set = compression_decompression[knapsack.compression][
            "compression"
        ](packed.descriptor_set)
        packed.message = compression_decompression[knapsack.compression]["compression"](
            packed.message
        )
        estimated = knapsack.max_container - packed.ByteSize()

        if len(knapsack.messages) < knapsack.max_messages:
            for _ in range(knapsack.max_messages - len(knapsack.messages)):
                message = packaging.get_random_message()
                if message:
                    knapsack.add_message(message)

        if estimated >= 0:
            second_packed = knapsack.knapsack(estimated)
        else:
            second_packed = None

        while second_packed:

            if len(knapsack.messages) < knapsack.max_messages:
                for _ in range(knapsack.max_messages - len(knapsack.messages)):
                    message = packaging.get_random_message()
                    if message:
                        knapsack.add_message(message)

            packed.descriptor_set = recompress_with_additional_data(
                packed.descriptor_set, second_packed.descriptor_set
            )
            packed.message = recompress_with_additional_data(
                packed.message, second_packed.message
            )
            packed.descriptor_sizes.extend(second_packed.descriptor_sizes)
            packed.message_sizes.extend(second_packed.message_sizes)
            estimated = knapsack.max_container - packed.ByteSize()
            if estimated >= 0:
                second_packed = knapsack.knapsack(estimated)
            else:
                second_packed = None

        packages_counter += 1
        print(f"Result Package Size {packed.ByteSize() = }")
        print(f"Messages in package {len(packed.message_sizes) = }")
        print(f"Messages Remains {packaging.messages_num = }")
        print(f"Highest priority {max(knapsack.priority) = }")
        print(f"===")
        data.append(
            {
                "package_size": packed.ByteSize(),
                "package_messages": len(packed.message_sizes),
            }
        )

    collected_data = pd.DataFrame(data)
    collected_data.to_csv(
        f"/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_{alg}_{knapsack.max_container}.csv",
        index=False,
    )

    # self_describing.descriptor_set.append(descriptor_set)
    # target = Any()
    # target.Pack(message)
    # self_describing.message.append(target)
    # print(f'{self_describing.ByteSize() = }')
    # print(f'{message.ByteSize() = }')

    # self_describing_compressed.descriptor_set = brotli.compress(descriptors[0].SerializeToString()) + brotli.compress(descriptors[1].SerializeToString())
    # self_describing_compressed.descriptor_sizes.append(len(brotli.compress(descriptors[0].SerializeToString())))
    # self_describing_compressed.descriptor_sizes.append(len(brotli.compress(descriptors[1].SerializeToString())))
    # self_describing_compressed.message = brotli.compress(messages[0].SerializeToString()) + brotli.compress(messages[1].SerializeToString())
    # self_describing_compressed.message_sizes.append(len(brotli.compress(messages[0].SerializeToString())))
    # self_describing_compressed.message_sizes.append(len(brotli.compress(messages[1].SerializeToString())))
    # print(f'{self_describing_compressed.ByteSize() = }')

    # first_message_size = self_describing_compressed.message_sizes[0]
    # first_message = self_describing_compressed.message[:first_message_size]
    # decompressed_message: bytes = brotli.decompress(first_message)

    # first_descriptor_size = self_describing_compressed.descriptor_sizes[0]
    # first_descriptor_bytes = brotli.decompress(self_describing_compressed.descriptor_set[:first_descriptor_size])
    # first_descriptor = descriptor_pb2.FileDescriptorSet.FromString(first_descriptor_bytes)
    # message_class = get_message_class(first_descriptor)
    # message: Message = message_class()
    # message.ParseFromString(decompressed_message)
    # import pdb; pdb.set_trace()


def combine_message_with_struct_id(alg: str):
    global compression_algorithm, decompression_algorithm
    if alg == "brotli":
        compression_algorithm = brotli.compress
        decompression_algorithm = brotli.decompress
    if alg == "lzma":
        compression_algorithm = lzma.compress
        decompression_algorithm = lzma.decompress
    if alg == "gzip":
        compression_algorithm = gzip.compress
        decompression_algorithm = gzip.decompress
    if alg == "bz2":
        compression_algorithm = bz2.compress
        decompression_algorithm = bz2.decompress
    data = []
    packaging = Packaging()
    knapsack = KnapSackWithStructId()
    knapsack.compression = alg if alg else "no_compression"
    packages_counter = 0
    for dataset_name in datasets:
        packaging.add_df(dataset_name)

    packaging.generate(descriptors_only=True)
    messages = []
    for _ in range(knapsack.max_messages):
        message = packaging.get_random_message()
        if message:
            messages.append(message)

    knapsack.add_messages(messages)
    while packages_counter < 500:
        if len(knapsack.messages) < knapsack.max_messages:
            for _ in range(knapsack.max_messages - len(knapsack.messages)):
                message = packaging.get_random_message()
                if message:
                    messages.append(message)
        packed = knapsack.knapsack()
        packed.message = compression_decompression[knapsack.compression]["compression"](
            packed.message
        )
        estimated = knapsack.max_container - packed.ByteSize()
        if len(knapsack.messages) < knapsack.max_messages:
            for _ in range(knapsack.max_messages - len(knapsack.messages)):
                message = packaging.get_random_message()
                if message:
                    knapsack.add_message(message)
        if estimated >= 0:
            second_packed = knapsack.knapsack(estimated)
        else:
            second_packed = None
        while second_packed:
            if len(knapsack.messages) < knapsack.max_messages:
                for _ in range(knapsack.max_messages - len(knapsack.messages)):
                    message = packaging.get_random_message()
                    if message:
                        knapsack.add_message(message)

            packed.message = recompress_with_additional_data(
                packed.message, second_packed.message
            )
            packed.message_sizes.extend(second_packed.message_sizes)
            packed.struct_id.extend(second_packed.struct_id)
            estimated = knapsack.max_container - packed.ByteSize()
            if estimated >= 0:
                try:
                    second_packed = knapsack.knapsack(estimated)
                except Exception:
                    second_packed = None
            else:
                second_packed = None

        packages_counter += 1
        print(f"Result Package Size {packed.ByteSize() = }")
        print(f"Messages in package {len(packed.message_sizes) = }")
        print(f"Messages Remains {packaging.messages_num = }")
        print(
            f"Highest priority = {max(knapsack.priority) if knapsack.priority else 0}"
        )
        print(f"===")
        data.append(
            {
                "package_size": packed.ByteSize(),
                "package_messages": len(packed.message_sizes),
            }
        )

    collected_data = pd.DataFrame(data)
    collected_data.to_csv(
        f"/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_{alg}_no_descriptors_{knapsack.max_container}.csv",
        index=False,
    )


import argparse

if __name__ == "__main__":
    # subprocess.run(["mkdir", "-p", f"{GENERATED_PATH}/generated"])
    parser = argparse.ArgumentParser()
    parser.add_argument("compression")
    args = parser.parse_args()

    combine_self_described_message(args.compression)
    # combine_message_with_struct_id(args.compression)
    # subprocess.run(["rm", "-rf", f"{GENERATED_PATH}/generated"])
