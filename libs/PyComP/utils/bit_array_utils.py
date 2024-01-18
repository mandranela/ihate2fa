import bitarray
from bitarray.util import ba2int, int2ba
from typing import Tuple
import numpy as np

BITARRAY = bitarray.bitarray


def int_to_bitarray(x: int, bit_width=None) -> BITARRAY:
    """
    Converts int to bits.
    
    Parameters:
        x: int
            integer to be converted
        bit_width: int, default = None
            length 
    Returns:
        bit: BITARRAY
            binary equivalent of x
    """
    assert isinstance(x, int)
    return int2ba(int(x), length=bit_width)


def bitarray_to_int(bit_array: BITARRAY):
    """
    Converts bitarray to int.
    
    Parameters:
        bit_array: BITARRAY
            bits to be converted
    Returns:
        dec: int
            decimal_equivalent of bit_array
    """
    return ba2int(bit_array)


def float_to_bitarrays(x: float, max_precision: int) -> Tuple[BITARRAY, BITARRAY]:
    """
    Convert floating point number to binary with the given max_precision
    Utility function to obtain binary representation of the floating point number.
    We return a tuple of binary representations of the integer part and the fraction part of the
    floating point number.

    Parameters:
        x: float
            input floating point number
        max_precision: int 
            max binary precision (after the decimal point) to which we should return the bitarray
    Returns:
        Tuple[BitArray, BitArray]: returns (uint_x_bitarray, frac_x_bitarray)
    """

    # find integer, fraction part of x
    uint_x = int(x)
    frac_x = x - int(x)

    # obtain binary representations of integer and fractional parts
    int_x_bitarray = int_to_bitarray(uint_x)
    frac_x_bitarray = int_to_bitarray(
        int(frac_x * np.power(2, max_precision)), bit_width=max_precision
    )
    return int_x_bitarray, frac_x_bitarray


def bitarrays_to_float(uint_x_bitarray: BITARRAY, frac_x_bitarray: BITARRAY) -> float:
    """Converts bitarrays corresponding to integer and fractional part of a floatating point number to a float.

    Parameters:
        uint_x_bitarray: BitArray 
            bitarray corresponding to the integer part of x
        frac_x_bitarray: BitArray 
            bitarray corresponding to the fractional part of x
    Returns:
        x: float, the floating point number 
    """
    # convert uint_x_bitarray to the integer part of the float
    uint_x = bitarray_to_int(uint_x_bitarray)

    # convert frac_x_bitarray to the fractional part of the float
    precision = len(frac_x_bitarray)
    frac_x = bitarray_to_int(frac_x_bitarray) / (np.power(2, precision))

    return uint_x + frac_x
