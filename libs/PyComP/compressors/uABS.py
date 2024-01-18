from math import ceil, floor, log2
import sys

class uABS:

    def __init__(self, p) -> None:
        self.p = p

    def shannon_entropy(self):
        self.entropy =  self.p*log2(1/self.p) + (1-self.p) * log2(1/(1-self.p))
        return self.entropy
    
    def uABS_encode_step(self, s: str, x_prev: int):
        if s == '0':
            x = ceil((x_prev + 1)/(1-self.p)) - 1
        if s == '1':
            x = floor(x_prev/self.p)
        return x

    def encode(self, msg :str, initial_state = 0):
        x = initial_state
        for i in msg: 
            assert i == '0' or i == '1'
            x = self.uABS_encode_step(i, x)
        return x, len(msg)
    
    def uABS_decode_step(self, x):
        s = ceil((x+1)*self.p) - ceil(x*self.p)
        if str(s) == '0':
            x_prev = floor(x*(1-self.p))
        if str(s) == '1':
            x_prev = ceil(x*self.p)
        return s, x_prev
    
    def decode(self, final_state, msg_len: int):
        symbols = []
        x_prev = final_state
        while len(symbols) !=  msg_len:
            s, x_prev = self.uABS_decode_step(x_prev)
            symbols.append(s)
        return list(reversed(symbols))