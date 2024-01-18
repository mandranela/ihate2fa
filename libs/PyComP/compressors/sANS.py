from PyComP.core.data import *
from PyComP.compressors.ANS import *
from PyComP.utils.bit_array_utils import int_to_bitarray, bitarray_to_int
import bitarray


class sANS(Data):
    '''
    sANS compressor and decompressor class. Inherits the data class.
    Initializes the rANS class. 
    Attributes:
        symbols: list
                list of all possible symbols
        frequency: list
                list of symbol frequency
    '''

    def __init__(self, symbols: list, frequency: list) -> None:
        super().__init__(symbols, frequency)
        self.rans = rANS(self.symbols, self.frequency)
        self.__get_interval()
        self.b = bitarray.bitarray()

    def __get_interval(self):
        self.all_interval = {}
        for s in self.symbols:
            self.all_interval[s] = range(
                self.freq_dist[s], 2 * self.freq_dist[s])

    def encode(self, msg: list):
        '''
        sANS encode function 

        Parameters:
            msg: list
                data to be encoded. Has to be a list
            initial_state: int
                initial state must be >= sum of freq
        Returns:
            final_state: int 
                final encoded value
            bit_output: bitarray.bitarray
                bit output from rescaling
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [5, 5, 2]
        >>> a = sANS(symbols, freq)
        >>> a.encode(['a', 'b', 'c', 'c', 'a', 'b'], 14)
        18 bitarray('00110011010')
        '''
        x = self.M + 2

        for s in msg:
            s_interval = self.all_interval[s]
            while x not in s_interval:
                self.b.append(x % 2)
                x = x//2
            x = self.rans.rANS_encode_step(s, x)
        return bin(x), self.b

    def decode(self, x: str, bit_array: bitarray.bitarray):
        '''
        sANS decode function

        Parameters: 
            encoded_value: int
                final state after encoding 
                this function inherits the probability distribuiton of the symbols.
                This function assumes that the probability distribuiton is know and the class is instantiated
            bit_array: bitarray.bitarray
                the bit output from renormalization
        Returns:
            symbols: list
                the decoded symbols in reverse order
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [5, 5, 2]
        >>> a = rANS(symbols, freq)
        >>> a.decode(18, bitarray.bitarray('00110011010'))
        ['a', 'b', 'c', 'c', 'a', 'b']
        '''
        decoded_symbols = []
        x = int(x, 2)
        while len(bit_array) != 0:
            s, x = self.rans.rANS_decode_step(x)
            decoded_symbols.append(s)
            while x not in range(self.M, 2*self.M):
                x = 2 * x + int(bit_array[-1])
                bit_array = bit_array[:-1]
        return list(reversed(decoded_symbols))


class sANSDecoder(Data):
    '''
    rANSDecoder class for decoding given symbols and frequency.
    initializes the sANS class. 
    Parmaeters:
        symbols: list
                a list of symbols
        frequency: list
                frequency distribuiton list
    '''

    def __init__(self, symbols: list, frequency: list) -> None:
        super().__init__(symbols, frequency)
        self.sans = sANS(self.symbols, self.frequency)

    def decode(self, x: str, bit_array: bitarray.bitarray):
        '''
        Function to decode, give the correct order
        Parameters: 
            encoded_value: int
                    final state after encoding
        Returns:
            decoded symbols: list
                list of decoded symbols
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [5, 5, 2]
        >>> a = sANSDecoder(symbols, freq)
        >>> a.decode(18, bitarray.bitarray('00110011010'))
        ['a', 'b', 'c', 'c', 'a', 'b']
        '''
        decoded_symbols = self.sans.decode(x, bit_array)
        return decoded_symbols