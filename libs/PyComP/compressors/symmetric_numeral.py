from PyComP.core.data import *
from math import log2
class SymmetricNumeral:
    '''
    Class for symmetric numeral encoding.

    Attributes: 
        base: int
            base of numeral system
    '''
    def __init__(self,  base: int) -> None:
        self.base = base

    def shannon_entropy(self):
        '''
        Computes the shannon's entorpy for the base

        Retuns: float
            entropy
        >>> s = SymmetricNumeral(7)
        >>> s.shannon_entropy()
        2.807354922057604
        '''
        return -log2(1/self.base)

    def encode(self, message:list):
        '''
        Encodes a set of symbols as per the base

        Parameters: 
            message: list
                list of digits of base b
        Returns: 
            encoded_value: base_b
                encoding of message in base b
        >>> s = SymmetricNumeral(7)
        >>> s.encode([1, 4, 5, 2, 5, 2, 6])
        197833
        '''
        x = 0
        for i in message:
            assert int(i) <= self.base - 1, "Invalid message for base"
            x = self.base * x + i
        return x  # in binary takes ceil(log(x))

    def decode(self, encoded_value):
        '''
        Decodes the encoded value as per as per the base

        Parameters:
            encoded_value: base_b
                list of digits of base b
        Returns: 
            decoded_symbols: base_b
                returns the decoded symbols
        >>> s = SymmetricNumeral(7)
        >>> s.decode(197833)
        [1, 4, 5, 2, 5, 2, 6]
        '''
        x = encoded_value
        decoded_list = []
        while x != int(x) % self.base:
            decoded_list.append(int(x) % self.base)
            x = x // self.base
        decoded_list.append(x)
        return [i for i in reversed(decoded_list)]