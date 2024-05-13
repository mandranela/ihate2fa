import os
import zlib, gzip, bz2, lzma, brotli

GENERATED_PATH = os.getcwd()
XTOPROTO_PATH = os.path.dirname(os.path.abspath(__file__)) + "/bin/xtoproto"


compression_decompression = {
    "no_compression": {"compression": lambda x: x, "decompression": lambda x: x},
    "brotli": {"compression": brotli.compress, "decompression": brotli.decompress},
    "lzma": {"compression": lzma.compress, "decompression": lzma.decompress},
    "gzip": {"compression": gzip.compress, "decompression": gzip.decompress},
    "zlib": {"compression": zlib.compress, "decompression": zlib.decompress},
}   