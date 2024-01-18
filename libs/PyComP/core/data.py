import math


class Data:

    '''
    This is the main class. Every compression algorithm inherits this class.

    :param symbols: list of symbols, elements can be any format
    :type symobls: list
    :param frequency: frequency list associated with the list
    : type freqeuncy: list
            

    Methods
    -------
    __frequency_distribution()
            Computes the frequency distribution and created attributes freq_dist, M(sum of frequency)

    __cumul_distribution()
            Computes the cumulative distribution of a symbol
            Creates an attribute cum_dist: dictionary with range
                    {
                            s_1:[low, high]
                    }
    .. note:: __freqency_distribuiton and __cumul_distribution are initialized

    Raises
    -------
    ValueError
        If frequency and symbol list do not match. 
    '''

    def __init__(self, symbols: list, frequency: list) -> None:
        self.symbols = symbols
        self.frequency = frequency

        if self.symbols != None and self.frequency != None:
            if len(self.frequency) != len(self.symbols):
                raise ValueError("Expected same length")
    
            if len(set(self.symbols)) != len(self.symbols):
                raise Exception("Duplicate Symbols found")

            for d in self.frequency:
                if not isinstance(d, (int, float)):
                    raise ValueError("Expected int or float for frequency")

            self.__freq_distribution()
            self.__cumul_distribution()
            self.shannon_entropy()

    def __freq_distribution(self):
        '''
        Computes the frequency distribution
        function for when only symbols are given
        '''
        self.M = sum(self.frequency)
        self.freq_dist = {}
        for i, s in enumerate(self.symbols):
            self.freq_dist[s] = self.frequency[i]

    def __cumul_distribution(self):
        '''
        computes the cumulative distribuiton table
                computes an attribute cum_dist: dict
        '''
        temp_freq = 0
        self.cum_dist = {}
        for i, s in enumerate(self.symbols):
            self.cum_dist[s] = [temp_freq, temp_freq + self.frequency[i]]
            temp_freq += (self.frequency[i])

    def shannon_entropy(self, show_steps=False) -> float:
        ''' 
        Computes the shanon entroy as sum(p(x)log(p(x)))

        Parameters:
            show_steps: bool, default = False
                    Show the steps if bool is true
        Returns:
            entropy: float
            the entropy value
        >>> symbols = ['a', 'b', 'c', 'e']
        >>> frequency = [3, 4, 5, 1]
        >>> d = Data(symbols, frequency)
        >>> print(d.shannon_entropy())
            1.8262452584026092

        TODO: Implement show steps
        '''
        ent = 0

        for p in self.frequency:
            ent += p*math.log2(p/self.M)/self.M
        self.entropy = (-1) * ent
        return self.entropy
