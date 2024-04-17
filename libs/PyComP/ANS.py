from .core.data import *
from .utils.utils import *
from .utils.file_utils import *
from typing import Tuple

# states are not defined as python allows for infinite integer precision


class rANS(Data):
    '''
    rANS compressor and decompressor class. Inherits the data class.

    Attributes:
        symbols: list
                list of all possible symbols
        frequency: list
                list of symbol frequency
    '''

    def __init__(self, symbols: list, frequency: list) -> None:
        super().__init__(symbols, frequency)

    def __find_symbol(self, slot):
        '''
        search function for decoding
        follows: c[s]<= slot < c[s+1]
        '''
        for s in self.symbols:
            l = self.cum_dist[s][0]
            h = self.cum_dist[s][1]
            if slot >= l and slot < h:
                return s

    def rANS_encode_step(self, symbol, x_prev: int) -> int:
        '''Encoding step function'''
        block = x_prev // self.freq_dist[symbol]
        slot = self.cum_dist[symbol][0] + (x_prev % self.freq_dist[symbol])
        x = block * self.M + slot
        return x

    def encode(self, msg: list, start_state: int) -> Tuple[str, int]:
        '''
        rANS encode function 

        Parameters:
            data: list
                data to be encoded. Has to be a list
        Returns:
            final_state: int 
                final encoded value
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [5, 5, 2]
        >>> a = rANS(symbols, freq)
        >>> a.encode(['a', 'b', 'c', 'c', 'a', 'b'], 0)
        1242
        '''

        output_log = []
        # TODO: output log, check
        x = start_state
        for d in msg:
            x = self.rANS_encode_step(d, x)
        return bin(x), len(msg)

    def rANS_decode_step(self, x_next: int) -> tuple:
        '''
        Decoding step function
        '''
        block_id = x_next // self.M
        slot = x_next % self.M
        decoded_symb = self.__find_symbol(slot)
        x_prev = block_id * self.freq_dist[decoded_symb] + slot - (self.cum_dist[decoded_symb][0])
        return decoded_symb, x_prev

    def decode(self, encoded_value: str, msg_len) -> list:
        '''
        rANS decode function

        Parameters: 
            encoded_value: int
                    final state after encoding 
                    this function inherits the probability distribuiton of the symbols.
                    This function assumes that the probability distribuiton is know and the class is instantiated
        Returns:
            symbols: list
                the decoded symbols in reverse order
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [5, 5, 2]
        >>> a = rANS(symbols, freq)
        >>> a.decode(1242,6)
        ['a', 'b', 'c', 'c', 'a', 'b']
        '''
        x_prev = int(encoded_value, 2)
        symbols = []
        while len(symbols) != msg_len:
            block_id = x_prev // self.M
            slot = x_prev % self.M
            decoded_symb = self.__find_symbol(slot)
            symbols.append(decoded_symb)
            x_prev = block_id * self.freq_dist[decoded_symb] + slot -(self.cum_dist[decoded_symb][0])
        return list(reversed(symbols))

    def __rANS_encoding_table_for_a_symbol(self, symbol, final_state: int):
        output__log = []
        for i in range(final_state):
            x = self.encode(msg=[symbol], start_state=i)
            output__log.append([symbol, int(i), int(x)])
        return output__log

    def rANS_encoding_table(self, final_state)-> pd.DataFrame:
        '''
        Returns the rANS encoding table. The format is similar to Dudak's paper. 
        Parameters:
            final_state: the final state table should contain
        Returns: 
            table: pd.Dataframe
                returns and pandas dataframe and prints the dataframe. 
        '''
        table_elements = []
        symbols = self.freq_dist.keys()
        for s in symbols:
            output = self.__rANS_encoding_table_for_a_symbol(s, final_state)
            for i in output:
                table_elements.append(i)
        table = encoding_table(table_elements)
        print(table)
        return table


class rANSDecoder(Data):
    '''
    rANSDecoder class for decoding given symbols and frequency.

    Parmaeters:
        symbols: list
                a list of symbols
        frequency: list
                frequency distribuiton list
    '''

    def __init__(self, symbols: list, frequency: list) -> None:
        super().__init__(symbols, frequency)
        self.rans = rANS(self.symbols, self.frequency)

    def decode(self, encoded_value: str, msg_len: int):
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
        >>> a = rANSDecoder(symbols, freq)
        >>> a.decode(1242,6)
        ['a', 'b', 'c', 'c', 'a', 'b']
        '''
        symbols = self.rans.decode(encoded_value, msg_len)
        return symbols