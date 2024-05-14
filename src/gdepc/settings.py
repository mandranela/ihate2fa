import json
import os
import zlib, gzip, bz2, lzma, brotli


from functools import partial

from typing import Callable
import zlib, gzip, bz2, lzma, brotli, zstd, zopfli, liblzfse, nlzss11, deflate

import huffpy
from bitstring import BitArray

GENERATED_PATH = os.getcwd()
XTOPROTO_PATH = os.path.dirname(os.path.abspath(__file__)) + "/bin/xtoproto"
DATASETS_PATH = "/Users/vladislavkovazin/miem/gdepc/static/datasets"

compression_decompression = {
    "no_compression": {"compression": lambda x: x, "decompression": lambda x: x},
    "brotli": {"compression": brotli.compress, "decompression": brotli.decompress},
    "lzma": {"compression": lzma.compress, "decompression": lzma.decompress},
    "gzip": {"compression": gzip.compress, "decompression": gzip.decompress},
    "zlib": {"compression": zlib.compress, "decompression": zlib.decompress},
}





def compress_(message: bytes, compressor: Callable[[bytes], bytes]):
    return compressor(message)


def str_compressor(message: str, compressor: Callable[[str], bytes]):
    return compressor(message)

def zopfli_compressor(data: bytes) -> bytes:
    c = zopfli.ZopfliCompressor(zopfli.ZOPFLI_FORMAT_DEFLATE)
    return c.compress(data) + c.flush()

def huffman_encode_with_tree(data: str) -> bytes:
    coder = huffpy.HuffmanCoder()
    huffmanString, tree = coder.encode(data)
    huffmanBytes = coder.toBytes(huffmanString, tree)
    return bytes(huffmanBytes)

def huffman_encode_without_tree(data: str) -> bytes:
    coder = huffpy.HuffmanCoder()
    huffmanString, _ = coder.encode(data)
    bitstream = BitArray(bin=huffmanString)
    return bitstream.tobytes()

def expanded_huffman_encode_with_tree(data: str) -> bytes:
    try:
        redefined_data: dict = json.loads(data)
    except:
        redefined_data = None
    coder = huffpy.HuffmanCoder()
    if redefined_data:
        huffmanString, tree = coder.encode(data, structure=list(redefined_data.keys()))
    else:
        huffmanString, tree = coder.encode(data, structure=None)
    huffmanBytes = coder.toBytes(huffmanString, tree)
    return bytes(huffmanBytes)

def expanded_huffman_encode_without_tree(data: str) -> bytes:
    try:
        redefined_data: dict = json.loads(data)
    except:
        redefined_data = None
    coder = huffpy.HuffmanCoder()
    if redefined_data:
        huffmanString, _ = coder.encode(data, structure=list(redefined_data.keys()))
    else:
        huffmanString, _ = coder.encode(data, structure=None)
    bitstream = BitArray(bin=huffmanString)
    return bitstream.tobytes()

compression_dict = {
    "lzma": partial(compress_, compressor=lzma.compress),
    "zlib": partial(compress_, compressor=zlib.compress),
    "brotli": partial(compress_, compressor=brotli.compress),
    "bz2": partial(compress_, compressor=bz2.compress),
    "zstd": partial(compress_, compressor=zstd.compress),
    "zopfli": partial(compress_, compressor=zopfli_compressor),
    "liblzfse": partial(compress_, compressor=liblzfse.compress),
    "nlzss11": partial(compress_, compressor=nlzss11.compress),
}

text_compression = {
    "huffman_with_tree": partial(str_compressor, compressor=huffman_encode_with_tree),
    "huffman_without_tree": partial(str_compressor, compressor=huffman_encode_without_tree),
    "expanded_huffman_encode_without_tree": partial(str_compressor, compressor=expanded_huffman_encode_without_tree),
    "expanded_huffman_encode_with_tree": partial(str_compressor, compressor=expanded_huffman_encode_with_tree),
}

compression_deflate = {
    "deflate_gzip": partial(compress_, compressor=deflate.gzip_compress),
    "deflate_zlib": partial(compress_, compressor=deflate.zlib_compress),
}


datasets = {
    "beach_water": "beach_water_quality_automated_sensors_1.csv",
    "iot_temp": "iot_temp.csv",
    "concentration_data": "all_sites_combined_concentration_data_clean_version.csv",
}

test_structs_ids = {name: i for i, name in enumerate(datasets)}

compression_decompression = {
    "no_compression": {"compression": lambda x: x, "decompression": lambda x: x},
    "brotli": {"compression": brotli.compress, "decompression": brotli.decompress},
    "lzma": {"compression": lzma.compress, "decompression": lzma.decompress},
    "gzip": {"compression": gzip.compress, "decompression": gzip.decompress},
    "zlib": {"compression": zlib.compress, "decompression": zlib.decompress},
}
