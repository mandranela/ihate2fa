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
