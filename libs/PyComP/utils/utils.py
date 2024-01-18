import random
import numpy as np
import pandas as pd


def get_symbols(symbols: list, frequency: list, no_symbols: int) -> list:
    '''
    Get arbitrary number of symbols following a particular distribution. Uses inversion sampling to sampling symbols. Used to test compressors. 
    
    Parameters:
        symbols: list
            list of symbols 
        frequency: list
            list of freqency associated with a particular symbol 
        no_symbols: int
            number of symbols you want to sample
    Returns:
        symbols: list
            list of symbols following a particular distribution
    >>> get_symbols(['a', 'b', 'c', 'd', 'z'], [0.2,0.3,0.1,0.1,0.4], 10)
        ['z', 'a', 'b', 'b', 'z', 'z', 'b', 'b', 'b', 'a']
    '''
    sym = []
    M = sum(frequency)
    prob = [i/M for i in frequency]
    cum_freq = []
    cum = 0

    for p in prob:
        cum += p
        cum_freq.append(cum)
    # print(cum_freq)
    for _ in range(no_symbols):
        idx = __inversion_sampling(cum_freq)
        sym.append(symbols[idx])
    return sym


def __inversion_sampling(cum_freq):
    '''
    private function given a cumulative frequency as a list, returns the index for which r < CF. 
    the index can be used to index the symbols list to get the symbol. 
    '''
    r = random.random()
    # print(r)
    for i, f in enumerate(cum_freq):
        if r <= f:
            return i


def encode_symbols_to_integer(symbols: list):
    '''
    Encodes each symbol to a integer starting from 0. Helper function for encoding_table

    Parameters:
        symbols: list
            list of symbols to be encoded
    Returns:
        encoded_list: dict 
            dict with the encoded values as keys
    '''

    encoded_list = {}
    for i, s in enumerate(symbols):
        encoded_list[s] = i
    return encoded_list


def encoding_table(table_elements):
    '''
    Creates an encoding table given table elements for ANS. This table can be used to determing the symbol spread function. Helper function for ANS.rANS.encoding_table().

    Paramaters:
        table_elements: Tuple(symbols, x_prev, x_new)
            table elements is a list of symbol, x_prev, x_new
            encoding_table: matrix (A) of size len(symbol) * max(x_new) where A_{symbol,x_new} = x_prev 
    Returns: 
        table: pd.Dataframe
            the encoding table. Usually for ANS. 
    '''
    table_elements = np.array(table_elements)
    symbols = set(table_elements[:, 0])  # 0th column is the set of symbols
    encoded_symbols = encode_symbols_to_integer(symbols)
    m = len(symbols)  # = no.of rows
    # max of 2nd column is the x_new = no.of columns
    n = max(np.array(table_elements[:, 2], dtype=np.int32)) + int(1)
    A = np.full(shape=(m, n), dtype=object, fill_value='-')
    for i in table_elements:
        i_index = int(encoded_symbols[i[0]])
        j_index = int(i[2])
        A[i_index, j_index] = i[1]
    df = pd.DataFrame(A, index=encoded_symbols.keys())
    return df


def convert_list_to_string(l: list)-> str:
    s = ''
    for i in l:
        s += i
    return s