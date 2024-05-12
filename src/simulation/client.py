from asyncio import Queue
import json
from packaging.proto import package_compressed_pb2
from packaging.main import get_message_class
from google.protobuf.message import Message
from settings import compression_decompression
from google.protobuf import descriptor_pb2
from google.protobuf.json_format import MessageToDict


class Client:

    iridium_comm: Queue[bytes]

    def __init__(self, compression: str):
        self.iridium_comm = Queue()
        self.compression = compression

    async def main(self):
        with open(
            "/Users/vladislavkovazin/miem/gdepc/src/simulation/tmp_db_file.txt", "w+"
        ) as file:
            while True:

                message_data = await self.iridium_comm.get()

                proto_object: Message = (
                    package_compressed_pb2.SelfDescribingCompressedMessage()
                )
                proto_object.ParseFromString(message_data)

                proto_object.message = compression_decompression[self.compression][
                    "decompression"
                ](proto_object.message)
                proto_object.descriptor_set = compression_decompression[
                    self.compression
                ]["decompression"](proto_object.descriptor_set)
                message_pointer = 0
                descriptor_pointer = 0
                for index in range(len(proto_object.message_sizes)):
                    message_size = proto_object.message_sizes[index]
                    sensor_message_bytes = proto_object.message[
                        message_pointer : message_pointer + message_size
                    ]
                    sensor_message_raw: bytes = compression_decompression[
                        self.compression
                    ]["decompression"](sensor_message_bytes)

                    descriptor_size = proto_object.descriptor_sizes[index]
                    descriptor_bytes = proto_object.descriptor_set[
                        descriptor_pointer : descriptor_pointer + descriptor_size
                    ]
                    descriptor_raw = compression_decompression[self.compression][
                        "decompression"
                    ](descriptor_bytes)
                    descriptor = descriptor_pb2.FileDescriptorSet.FromString(
                        descriptor_raw
                    )
                    message_class = get_message_class(descriptor)
                    message: Message = message_class()
                    message.ParseFromString(sensor_message_raw)
                    print(json.dumps(MessageToDict(message)), file=file)

                    message_pointer += message_size
                    descriptor_pointer += descriptor_size
