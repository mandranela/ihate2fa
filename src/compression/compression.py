from collections import Counter

import zlib, gzip, bz2, lzma

from PyComP import huffman, ANS, sANS, uABS, arithmetic_coding, symmetric_numeral, file_compressor


def compress_zlib(msg):
    c_msg = zlib.compress(msg)

    return c_msg


def compress_gzip(msg):
    c_msg = gzip.compress(msg)

    return c_msg


def compress_bz2(msg):
    c_msg = bz2.compress(msg)

    return c_msg


def compress_lzma(msg):
    c_msg = lzma.compress(msg)

    return c_msg
