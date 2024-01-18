import math
import tabulate
from PyComP.utils.ac_utils import *
from PyComP.core.data import *
from PyComP.utils.bit_array_utils import float_to_bitarrays, bitarrays_to_float
import bitarray
from typing import Tuple


class ArithmeticCoding(Data):
    '''
    Class for arithmetic coding compression with out rescaling. Might not be efficient. Inherits the data class. Allows compression in two ways.

    1. By specifying the symbols and frequency.
        In this case arg:msg must be provided in the encode step. 
    2. By giving the entire message itself. 
        No argument required in the encode step. 
        Computes the probability and cumulative distribution from the message itself. 

    Attributes:
        symbols : list
            list of symbols, elements can be any format

        frequency: list
            frequency list associated with the list
        
        message: list, default = None
            list of message. 
    '''

    def __init__(self, symbols: list, frequency: list, message: list =None) -> None:
        super().__init__(symbols, frequency)
        self.message = message
        if self.message != None:
            self.__prob_dist()
            self.__cumul_distribution()
        else: ## this is required as AC works with probabilities not freq
            self.M = sum(self.freq_dist.values())
            for i in self.symbols:
                self.freq_dist[i] = self.freq_dist[i]/self.M
                self.cum_dist[i] = [self.cum_dist[i][0]/self.M, self.cum_dist[i][1]/self.M]

    def __prob_dist(self):
        self.symbols = []
        self.prob_dist = {}
        self.num_elements = 0
        for i in self.message:
            self.symbols.append(i)
            try:
                self.prob_dist[i] += 1
            except:
                self.prob_dist[i] = 1
            self.num_elements += 1

        for key in self.prob_dist.keys():
            self.prob_dist[key] = self.prob_dist[key]/self.num_elements

    def __cumul_distribution(self):
        self.cum_dist = {}
        temp_freq = 0
        for symbol, freq in self.prob_dist.items():
            self.cum_dist[symbol] = [temp_freq,(temp_freq + freq)]  # storing high and low
            temp_freq += freq

    def msg_prob(self, message: list) -> float:
        '''
        Computes the joint probability of message. Requires the class to initianted. 
            P(x_1, x_2, ...) = p(x_1).p(x_2). ...
        
        Parameters:
            message: list
        Returns:
            prob: float
                the probability of the entire message
        >>> f = ArithmeticCoding(['a', 'b', 'c'], [0.8, 0.02, 0.18])
        >>> f.msg_prob('aabcca')
        0.0003317760000000001
        '''
        self.prob = 1
        for s in message:
            assert (str(s) in self.symbols)
            self.prob *= self.freq_dist[s]/self.M

        self.lx = abs(math.ceil(math.log2(self.prob))) + 1
        return self.prob

    def encode(self, msg: list = None, show_steps: bool = False) -> Tuple[bitarray.bitarray, int]:
        '''
        Arithmetic encoding function. Can be used to encdoe in either ways as specifiec before. 

        Parameters:
            msg: list, default = None
                message you want to encode
            show_steps: bool, default = False
                shows the encoding step
        Returns: 
            encoded_value: BITARRAY
                binary string of the encoded value.
            lenght: int
                length of the message. To specify for decoder. 
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [0.8, 0.02, 0.18]
        >>> f = ArithmeticCoding(symbols, freq)
        >>> encoded_value, msg_len = f.encode('abaca')
        >>> print(encoded_value, msg_len)
        bitarray('10100110110') 5

        >>> f = ArithmeticCoding(symbols = None, frequency= None, message='hello')
        >>> encoded_value, msg_len = f.encode(show_steps = True)
        Encoding Process
        ------------------
        +--------+--------------------------------------------+------------------+
        | Symbol |                  Interval                  |      Remark      |
        +--------+--------------------------------------------+------------------+
        |   h    |                  (0, 0.2)                  | Pick Next Symbol |
        |   he   | (0.04000000000000001, 0.08000000000000002) | Pick Next Symbol |
        |  hel   | (0.05600000000000001, 0.07200000000000001) | Pick Next Symbol |
        |  hell  | (0.06240000000000001, 0.06880000000000001) | Pick Next Symbol |
        | hello  | (0.06752000000000001, 0.06880000000000001) | Pick Next Symbol |
        |        |            Symbols Encoded = 5             |                  |
        |        |         Tag = 0.06816000000000001          |                  |
        |        | Compressed Value = bitarray('00010001011') |                  |
        +--------+--------------------------------------------+------------------+
        '''

        if show_steps == True:
            output = []

        low_old = 0
        high_old = 1
        range = 1
        if msg == None:
            msg = self.message
        # self.__symbol_prob(symbols)  ## computes the truncation value
        sym = ''
        output_sym = ''  # output from encoding process
        for i, s in enumerate(msg):
            sym += s
            if s not in self.symbols:
                raise ValueError("Invalid symbol")

            interval = self.cum_dist[s]

            low = low_old + range * interval[0]
            high = low_old + range * interval[1]

            if show_steps == True:
                output.append([sym, (low, high), "Pick Next Symbol"])

            range = high - low

            low_old = low
            high_old = high

        # print(low_old, high_old)
        self.tag = (low_old + high_old)/2
        k = math.ceil(-math.log2(high-low)) + 1
        # tag_to_bin = decToBinConversion(self.tag, self.lx - len(output_sym))
        _, tag_to_bin = float_to_bitarrays(self.tag, k)  # binary conversion of 0.5

        self.encoded_value = tag_to_bin

        if show_steps==True:
            output.append(
                [' ', f"Symbols Encoded = {i+1}\nTag = {self.tag}\nCompressed Value = {self.encoded_value}"])
            print("\nEncoding Process")
            print("------------------")
            print(tabulate.tabulate(output, headers=[
                  'Symbol', 'Interval', 'Remark'], tablefmt="pretty", numalign='center'))
        
            # print("Encoded value \n-------------\n", self.encoded_value)

        return self.encoded_value, len(msg)

    def __return_symbol(self, tag):
        ''' 
        Given a tag returns the corresponding symbol
        '''
        for key, value in self.cum_dist.items():

            if tag < value[1]:
                '''
                intervals are disjoints
                '''
                return (key, value)

    def decode(self, encoded_value: bitarray.bitarray, msg_length: int, show_steps: bool = False):
        '''
        Using the decoding by checking interval, updating interval, and picking new symbol. 
       
        Parameters: 
            encoded_value: bitarray.bitarray
                bitarray instance of the encoded value. 
            msg_length: int
                length of the message. needs to be specified to the same number as original msg to get right decoding. 
            show_steps: bool, default = False
                shows decoding steps. 
        Returns:
            decoded_symbols: str
                returns the decoded symbols

        >>> symbols = ['a', 'b', 'c']
        >>> freq = [0.8, 0.02, 0.18]
        >>> f = ArithmeticCoding(symbols, freq)
        >>> encoded_value, msg_len = f.encode('abaca')
        >>> decoded_value = f.decode(encoded_value, msg_len)
        >>> print(decoded_value)
        abaca

        >>> decoded_value = f.decode(encoded_value, msg_len, show_steps=True)
        Decoding Process
        ------------------
        +--------------+-------------------------+---------------+--------------------------------------------+-----------+
        | Decoded Symb |      Encoded Value      |      Tag      |                   Range                    |  Remark   |
        +--------------+-------------------------+---------------+--------------------------------------------+-----------+
        |      h       | bitarray('00010001011') | 0.06787109375 |                  (0, 0.2)                  | Pick next |
        |      he      | bitarray('00010001011') | 0.06787109375 | (0.04000000000000001, 0.08000000000000002) | Pick next |
        |     hel      | bitarray('00010001011') | 0.06787109375 | (0.05600000000000001, 0.07200000000000001) | Pick next |
        |     hell     | bitarray('00010001011') | 0.06787109375 | (0.06240000000000001, 0.06880000000000001) | Pick next |
        |    hello     | bitarray('00010001011') | 0.06787109375 | (0.06752000000000001, 0.06880000000000001) | Pick next |
        +--------------+-------------------------+---------------+--------------------------------------------+-----------+
        Decoded Value = hello

        '''
        if show_steps == True:
            output = []

        t = bitarrays_to_float(bitarray.bitarray('0'), encoded_value)
        decoded_symbols = ''
        low_old = 0
        high_old = 1
        ran = 1
        for i in range(msg_length):
            t_prime = (t - low_old)/(ran)

            symb, interval = self.__return_symbol(t_prime)
            decoded_symbols += symb

            low = low_old + ran * interval[0]
            high = low_old + ran * interval[1]

            ran = high - low

            low_old = low
            high_old = high
            if show_steps == True:
                output.append([decoded_symbols, encoded_value,
                              t, (low, high), "Pick next\n"])
        # print(low_old, high_old)

        if show_steps == True:
            print("\nDecoding Process")
            print("------------------")
            print(tabulate.tabulate(output, headers=[
                  'Decoded Symb', 'Encoded Value', 'Tag', 'Range', 'Remark'], tablefmt="pretty", numalign='center'))
            print(f"Decoded Value = {decoded_symbols}\n")

        return decoded_symbols

class ArithmeticDecoder(Data):
    '''
    Arithmetic decoder class. Used only for decoing. Assume a communication channel where the receiver has access to the decoding channel only. instantiates the arithmetic coding class and uses the decoding function. 

    Attributes:
        symbols : list
            list of symbols, elements can be any format

        frequency: list
            frequency list associated with the list
    >>> symbols = ['a', 'b', 'c']
    >>> freq = [0.8, 0.02, 0.18]
    >>> f = ArithmeticDecoder(symbols, freq)
    >>> f.decode(bitarray.bitarray('10100110110'),5)
    abaca
    '''
    def __init__(self, symbols: list, frequency: list) -> None:
        super().__init__(symbols, frequency)
        self.arithmetic_coding = ArithmeticCoding(self.symbols, self.frequency)

    def decode(self, encoded_value: bitarray.bitarray, msg_length: int):
        '''
        Decodes a bit array using airithmetic coding scheme. 
        Parameters: 
            encoded_value: bitarray.bitarray
                bitarray instance of the encoded value. 
            msg_length: int
                length of the message. needs to be specified to the same number as original msg to get right decoding.  
        Returns:
            decoded_symbols: str
                returns the decoded symbols
        '''
        symbols = self.arithmetic_coding.decode(encoded_value, msg_length)
        return symbols


class RangeCoding(ArithmeticCoding):
    '''
    Class for arithmetic coding compression with rescaling. Might not be efficient. Inherits the arithmetic coding class and changes teh encoding and decodign function. Allows compression in two ways.

    1. By specifying the symbols and frequency.
        In this case arg:msg must be provided in the encode step. 
    2. By giving the entire message itself. 
        No argument required in the encode step. 
        Computes the probability and cumulative distribution from the message itself. 

    Attributes:
        symbols : list
            list of symbols, elements can be any format

        frequency: list
            frequency list associated with the list
        
        message: list, default = None
            list of message. 
    '''

    def __init__(self, symbols: list, frequency: list, message:str=None) -> None:
        super().__init__(symbols, frequency, message)

    def __left_scale(self, x: float):
        return 2 * x

    def __right_scale(self, x: float):
        return 2 * x - 1
    
    def __return_symbol(self, tag):
        ''' 
        Given a tag returns the corresponding symbol
        '''
        for key, value in self.cum_dist.items():

            if tag < value[1]:
                '''
                intervals are disjoints
                '''
                return (key, value)

    def encode(self, msg: list = None,  show_steps : bool =False) -> Tuple[bitarray.bitarray, int]:
        '''
        Range encoding function. Can be used to encdoe in either ways as specifiec before. 

        Parameters:
            msg: list, default = None
                message you want to encode
            show_steps: bool, defalut = False
                shows encoding step
        Returns: 
            encoded_value: BITARRAY
                binary string of the encoded value.
            lenght: int
                length of the message. To specify for decoder. 
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [0.8, 0.02, 0.18]
        >>> f = RangeCoding(symbols, freq)
        >>> encoded_value, msg_len = f.encode('abaca')
        >>> print(encoded_value, msg_len)
        bitarray('1010011011') 5

        >>> f = RangeCoding(symbols = None, frequency= None, message='hello', show_steps=True)
        >>> encoded_value, msg_len = f.encode()
        Encoding Process
        ------------------
        +--------+--------------------------------------------+------------------+
        | Symbol |                  Interval                  |      Remark      |
        +--------+--------------------------------------------+------------------+
        |   h    |                  (0, 0.2)                  |  Left Scaling    |
        |        |                                            |    Output = 0    |
        |   h    |                  (0, 0.4)                  |  Left Scaling    |
        |        |                                            |    Output = 0    |
        |   h    |                  (0, 0.8)                  | Pick Next Symbol |
        |   he   | (0.16000000000000003, 0.32000000000000006) |  Left Scaling    |
        |        |                                            |    Output = 0    |
        |   he   | (0.32000000000000006, 0.6400000000000001)  | Pick Next Symbol |
        |  hel   | (0.44800000000000006, 0.5760000000000001)  | Pick Next Symbol |
        |  hell  |  (0.4992000000000001, 0.5504000000000001)  | Pick Next Symbol |
        | hello  |  (0.5401600000000001, 0.5504000000000001)  |  Right Scaling   |
        |        |                                            |    Output = 1    |
        | hello  | (0.08032000000000017, 0.10080000000000022) |  Left Scaling    |
        |        |                                            |    Output = 0    |
        | hello  | (0.16064000000000034, 0.20160000000000045) |  Left Scaling    |
        |        |                                            |    Output = 0    |
        | hello  |  (0.3212800000000007, 0.4032000000000009)  |  Left Scaling    |
        |        |                                            |    Output = 0    |
        | hello  |  (0.6425600000000014, 0.8064000000000018)  |  Right Scaling   |
        |        |                                            |    Output = 1    |
        | hello  |  (0.2851200000000027, 0.6128000000000036)  | Pick Next Symbol |
        |        |            Symbols Encoded = 5             |                  |
        |        |  Rescaling Output = bitarray('000100011')  |                  |
        |        |                 Tag = 0.5                  |                  |
        |        |  Compressed Value = bitarray('000100011')  |                  |
        +--------+--------------------------------------------+------------------+
        '''

        if show_steps == True:
            output = []
        low_old = 0
        high_old = 1
        range = 1
        msg = self.message if msg == None else msg

        # self.__symbol_prob(symbols)  ## computes the truncation value
        sym = ''
        output_sym = bitarray.bitarray()  # rescaling output
        for i, s in enumerate(msg):
            sym += s
            if s not in self.symbols:
                raise ValueError(
                    "Value symbol not fround in prob distribuiton")

            interval = self.cum_dist[s]

            low = low_old + range * interval[0]
            high = low_old + range * interval[1]
            while (high < 0.5 and low < 0.5) or (high > 0.5 and low > 0.5):
                if low > 0.5 and high > 0.5:
                    output_sym.append(1)
                    if show_steps == True:
                        output.append(
                            [sym, (low, high), "Right Scaling \nOutput = 1"])
                    low = self.__right_scale(low)
                    high = self.__right_scale(high)

                elif high < 0.5 and low < 0.5:
                    output_sym.append(0)
                    if show_steps == True:
                        output.append(
                            [sym, (low, high), "Left Scaling \nOutput = 0"])
                    low = self.__left_scale(low)
                    high = self.__left_scale(high)

            if show_steps == True:
                output.append([sym, (low, high), "Pick Next Symbol"])

            range = high - low

            low_old = low
            high_old = high

        # print(low_old, high_old)
        # since 0.5 always lies between high and low because we rescale even after the last symbol encoding.
        self.tag = 0.5

        # tag_to_bin = decToBinConversion(self.tag, self.lx - len(output_sym))
        tag_to_bin = bitarray.bitarray(1)  # binary conversion of 0.5
        self.encoded_value = output_sym
        self.encoded_value.append(1)

        if show_steps == True:
            output.append(
                [' ', f"Symbols Encoded = {i+1}\nRescaling Output = {output_sym}\nTag = {self.tag}\nCompressed Value = {self.encoded_value}"])
            print("\nEncoding Process")
            print("------------------")
            print(tabulate.tabulate(output, headers=[
                  'Symbol', 'Interval', 'Remark'], tablefmt="pretty", numalign='center'))
    

        return self.encoded_value, len(msg)

    def decode(self, encoded_value: bitarray.bitarray, msg_length: int, show_steps: bool = False):
        '''
        Using the decoding by checking interval, rescaling, updating interval, and picking new symbol. 
       
        Parameters: 
            encoded_value: bitarray.bitarray
                bitarray instance of the encoded value. 
            msg_length: int
                length of the message. needs to be specified to the same number as original msg to get right decoding. 
            show_steps: bool, default = False
                shows decoding steps. 
        Returns:
            decoded_symbols: str
                returns the decoded symbols
        >>> symbols = ['a', 'b', 'c']
        >>> freq = [0.8, 0.02, 0.18]
        >>> f = RangeCoding(symbols, freq)
        >>> decoded_value = f.decode(bitarray.bitarray('1010011011'), 5)
        >>> print(decoded_value)
        abaca

        >>> decoded_value = f.decode(encoded_value, msg_len, show_steps=True)
        Decoding Process
        ------------------
        +--------------+-----------------------+-------------+--------------------------------------------+---------------+
        | Decoded Symb |     Encoded Value     |     Tag     |                   Range                    |    Remark     |
        +--------------+-----------------------+-------------+--------------------------------------------+---------------+
        |      h       | bitarray('000100011') | 0.068359375 |                  (0, 0.2)                  | Left Scaling  |
        |              |                       |             |                                            |   Remove 0    |
        |      h       | bitarray('00100011')  | 0.13671875  |                  (0, 0.4)                  | Left Scaling  |
        |              |                       |             |                                            |   Remove 0    |
        |      h       |  bitarray('0100011')  |  0.2734375  |                  (0, 0.8)                  |   Pick next   |
        |      he      |  bitarray('0100011')  |  0.2734375  | (0.16000000000000003, 0.32000000000000006) | Left Scaling  |
        |              |                       |             |                                            |   Remove 0    |
        |      he      |  bitarray('100011')   |  0.546875   | (0.32000000000000006, 0.6400000000000001)  |   Pick next   |
        |     hel      |  bitarray('100011')   |  0.546875   | (0.44800000000000006, 0.5760000000000001)  |   Pick next   |
        |     hell     |  bitarray('100011')   |  0.546875   |  (0.4992000000000001, 0.5504000000000001)  |   Pick next   |
        |    hello     |  bitarray('100011')   |  0.546875   |  (0.5401600000000001, 0.5504000000000001)  | Right Scaling |
        |              |                       |             |                                            |   Remove 1    |
        |    hello     |   bitarray('00011')   |   0.09375   | (0.08032000000000017, 0.10080000000000022) | Left Scaling  |
        |              |                       |             |                                            |   Remove 0    |
        |    hello     |   bitarray('0011')    |   0.1875    | (0.16064000000000034, 0.20160000000000045) | Left Scaling  |
        |              |                       |             |                                            |   Remove 0    |
        |    hello     |    bitarray('011')    |    0.375    |  (0.3212800000000007, 0.4032000000000009)  | Left Scaling  |
        |              |                       |             |                                            |   Remove 0    |
        |    hello     |    bitarray('11')     |    0.75     |  (0.6425600000000014, 0.8064000000000018)  | Right Scaling |
        |              |                       |             |                                            |   Remove 1    |
        |    hello     |     bitarray('1')     |     0.5     |  (0.2851200000000027, 0.6128000000000036)  |   Pick next   |
        +--------------+-----------------------+-------------+--------------------------------------------+---------------+
        Decoded Value = hello
        '''
        if show_steps== True:
            output = []
        t = bitarrays_to_float(bitarray.bitarray('0'), encoded_value)
        decoded_symbols = ''
        low_old = 0
        high_old = 1
        ran = 1
        for i in range(msg_length):
            t_prime = (t - low_old)/(ran)
            symb, interval = self.__return_symbol(t_prime)
            decoded_symbols += symb

            low = low_old + ran * interval[0]
            high = low_old + ran * interval[1]

            while (high < 0.5 and low <= 0.5) or (high > 0.5 and low >= 0.5):

                if low >= 0.5 and high > 0.5:

                    if show_steps == True:
                        output.append(
                            [decoded_symbols, encoded_value, t, (low, high), "Right Scaling\nRemove 1\n"])

                    encoded_value = encoded_value[1:]
                    enc_val_list = encoded_value.tolist()
                    enc = ''.join([str(elem) for elem in enc_val_list])
                    enc = '0.'+enc
                    t = getBinaryFractionValue(enc)

                    low = self.__right_scale(low)
                    high = self.__right_scale(high)

                elif high < 0.5 and low <= 0.5:
                    if show_steps == True:
                        output.append(
                            [decoded_symbols, encoded_value, t, (low, high), "Left Scaling\nRemove 0"])
                    encoded_value = encoded_value[1:]
                    enc_val_list = encoded_value.tolist()
                    enc = ''.join([str(elem) for elem in enc_val_list])

                    enc = '0.'+enc
                    t = getBinaryFractionValue(enc)

                    low = self.__left_scale(low)
                    high = self.__left_scale(high)

            ran = high - low

            low_old = low
            high_old = high
            if show_steps == True:
                output.append([decoded_symbols, encoded_value,
                              t, (low, high), "Pick next\n"])
        # print(low_old, high_old)

        if show_steps == True:
            print("\nDecoding Process")
            print("------------------")
            print(tabulate.tabulate(output, headers=[
                  'Decoded Symb', 'Encoded Value', 'Tag', 'Range', 'Remark'], tablefmt="pretty", numalign='center'))
            print(f"Decoded Value = {decoded_symbols}\n")
    
        return decoded_symbols

class RangeDecoder:
    '''
    Range decoder class. Used only for decoing. Assume a communication channel where the receiver has access to the decoding channel only. instantiates the range coding class and uses the decoding function. 

    Attributes:
        symbols : list
            list of symbols, elements can be any format

        frequency: list
            frequency list associated with the list
    >>> symbols = ['a', 'b', 'c']
    >>> freq = [0.8, 0.02, 0.18]
    >>> f = RangeDecoder(symbols, freq)
    >>> f.decode(bitarray.bitarray('1010011011'),5)
    abaca
    '''
    def __init__(self, symbols: list, frequency: list) -> None:
        self.symbols = symbols
        self.frequency = frequency
        self.coding_func = RangeCoding(symbols, frequency)

    def decode(self, encoded_value: bitarray.bitarray, msg_length: int):
        '''
        Decodes a bit array using airithmetic coding scheme. 
        Parameters: 
            encoded_value: bitarray.bitarray
                bitarray instance of the encoded value. 
            msg_length: int
                length of the message. needs to be specified to the same number as original msg to get right decoding.  
        Returns:
            decoded_symbols: str
                returns the decoded symbols
        '''
        symbols = self.coding_func.decode(encoded_value, msg_length)
        return symbols