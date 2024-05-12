from functools import partial

from typing import Callable
import zlib, gzip, bz2, lzma, brotli


def compress_(message: bytes, compressor: Callable[[bytes], bytes]):
    return compressor(message)


def str_compressor(message: str, compressor: Callable[[str], bytes]):
    return compressor(message)


compression_dict = {
    "lzma": partial(compress_, compressor=lzma.compress),
}

compression_dict.update(
    {
        f"zlib_{i}": partial(compress_, compressor=partial(zlib.compress, level=i))
        for i in range(-1, 10)
    }
)
compression_dict.update(
    {
        f"brotli_{i}": partial(
            compress_, compressor=partial(brotli.compress, quality=i)
        )
        for i in range(0, 12)
    }
)
compression_dict.update(
    {
        f"gzip_{i}": partial(
            compress_, compressor=partial(gzip.compress, compresslevel=i)
        )
        for i in range(0, 10)
    }
)
compression_dict.update(
    {
        f"bz2_{i}": partial(
            compress_, compressor=partial(bz2.compress, compresslevel=i)
        )
        for i in range(1, 10)
    }
)


datasets = [
    "beach_water_quality_automated_sensors_1",
    "beach_weather_stations_automated_sensors_1",
    "iot_network_logs",
    "iot_temp",
    "iotpond1",
    "iotpond10",
    "iotpond11",
    "iotpond12",
    "iotpond2",
    "iotpond3",
    "iotpond4",
    "iotpond6",
    "iotpond7",
    "iotpond8",
    "iotpond9",
]

test_structs_ids = {name: i for i, name in enumerate(datasets)}

compression_decompression = {
    "no_compression": {"compression": lambda x: x, "decompression": lambda x: x},
    "brotli": {"compression": brotli.compress, "decompression": brotli.decompress},
    "lzma": {"compression": lzma.compress, "decompression": lzma.decompress},
    "gzip": {"compression": gzip.compress, "decompression": gzip.decompress},
    "zlib": {"compression": zlib.compress, "decompression": zlib.decompress},
}
