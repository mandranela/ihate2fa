import json
import pandas as pd
import multiprocessing as mp
from parse import get_proto_message
from settings import compression_dict
import time
import logging

logging.basicConfig(level=logging.INFO)
parquete_compressions = ["snappy", "gzip", "brotli", "lz4", "zstd"]


def compress_message(index: int, message: pd.Series, columns: list):
    data = []
    t = time.process_time()

    jsoned = json.dumps(message.to_dict())
    jsoned_bytes = jsoned.encode()
    json_elapsed_time = time.process_time() - t

    data.append(
        {
            "message_index": index,
            "format": "json",
            "memory_usage": len(jsoned_bytes),
            "compression": "no_compression",
            "elapsed_time": json_elapsed_time,
        }
    )

    for compression in parquete_compressions:
        t = time.process_time()
        parquete_data = pd.DataFrame(message.to_dict(), index=columns).to_parquet(
            compression=compression
        )
        parquete_elapsed_time = time.process_time() - t

        data.append(
            {
                "message_index": index,
                "format": "parquete",
                "memory_usage": len(parquete_data),
                "compression": compression,
                "elapsed_time": parquete_elapsed_time,
            }
        )

    t = time.process_time()
    proto_messages = get_proto_message(message)
    proto_single_packed = proto_messages.SerializeToString()
    proto_elapsed_time = time.process_time() - t

    data.append(
        {
            "message_index": index,
            "format": "protobuf",
            "memory_usage": len(proto_single_packed),
            "compression": "no_compression",
            "elapsed_time": proto_elapsed_time,
        }
    )

    for compression, compressor in compression_dict.items():
        t = time.process_time()
        json_comperssed = compressor(jsoned_bytes)
        elapsed_time = time.process_time() - t
        data.append(
            {
                "message_index": index,
                "format": "json",
                "memory_usage": len(json_comperssed),
                "compression": compression,
                "elapsed_time": elapsed_time + json_elapsed_time,
            }
        )
        t = time.process_time()
        proto_comperssed = compressor(proto_single_packed)
        elapsed_time = time.process_time() - t
        data.append(
            {
                "message_index": index,
                "format": "protobuf",
                "memory_usage": len(proto_comperssed),
                "compression": compression,
                "elapsed_time": elapsed_time + proto_elapsed_time,
            }
        )

    return data


def dataset_compression(df: pd.DataFrame, name: str):
    data = []
    result = pd.DataFrame(
        columns=[
            "message_index",
            "format",
            "memory_usage",
            "compression",
            "elapsed_time",
        ]
    )
    with mp.Pool(mp.cpu_count()) as pool:
        messages_data = pool.starmap(
            compress_message,
            [(int(index), message, df.columns) for index, message in df.iterrows()],
        )
        for message_data in messages_data:
            data.extend(message_data)
    result = pd.DataFrame(data)
    result.to_csv(f'{name}_compression.csv')
