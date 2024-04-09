from collections import Counter

import zlib, gzip, bz2, lzma

from libs.PyComP import huffman, ANS, sANS, uABS, arithmetic_coding, symmetric_numeral


def compress(method: str, msg):
    match method:
        case "zlib":
            e_msg = zlib.compress()
        case "gzip":
            e_msg = gzip.compress()
        case "bz2":
            e_msg = bz2.compress()
        case "lzma":
            e_msg = lzma.compress()
        case "huffman":
            h = huffman.Huffman
            compressor = huffman()
