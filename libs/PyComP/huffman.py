from .core.data import *
from typing import Tuple
import numpy as np
from typing import Tuple
import tabulate
class Node:
    '''
    Class for a node.

    Attributes:
        symbols: str
            symbol of the node
        freq: int | float
            frequency of the node. For internal nodes calculated as sum of nodes
        left: Node, default: None
            left child of a node
        right: Node, default: None
            right child of a node
    '''
    def __init__(self, symbol:str, freq: Tuple[int, float, np.int32], left = None, right = None):
        self.symbol = symbol
        self.freq = freq
        self.left:Node = left
        self.right: Node = right
        self.code = ''


class Huffman(Data):
    '''
    Class for Huffman Encoding. This class inherits the data class.

    Attributes:
        symbols : list
            list of symbols, elements can be any format

        frequency: list
            frequency list associated with the list
        
        huffman_table: dict
            initialize as an empty dictionary. Datastructure for huffman code
    '''

    def __init__(self, symbols: list, frequency: list) -> None:
        
        super().__init__(symbols, frequency)
        self.huffman_table = {}
        self.__leaf_nodes()

    def __leaf_nodes(self):
        self.nodes = []
        for s in self.symbols:
            self.nodes.append(Node(s, self.freq_dist[s]/self.M))

    def huffman_tree(self) -> Node:
        '''
        Using the recursive huffman's technique creates a huffman tree. 

        Returns:
            root_node: Node
                returns the root node. The tree can be constructed from the root node as it internal nodes are childrens. 
        '''
        while len(self.nodes) > 1:
            # sort all the nodes
            self.nodes = sorted(self.nodes, key=lambda x: x.freq)

            # pick smallest 2 nodes
            right: Node = self.nodes[0]
            left: Node = self.nodes[1]

            left.code = 0
            right.code = 1

            # combine the 2 smallest nodes
            newNode = Node('('+left.symbol+right.symbol+')',
                           left.freq+right.freq, left, right)
            self.nodes.remove(left)
            self.nodes.remove(right)
            self.nodes.append(newNode)

        self.root_node = self.nodes[0]  # root node
        return self.root_node

    def __get_codes(self, node:Node, val='')->dict:
        '''
        private function: Gets the codewords by traversing depth first the huffman tree. The left edge is 0 and right edge is 1

        Parameters:
            node: Node
                Takes in a node
        Returns:
            huffman_table: dict
        '''
        
        newVal = val + str(node.code)

        if (node.left):
            self.__get_codes(node=node.left, val=newVal)
        if (node.right):
            self.__get_codes(node=node.right, val=newVal)

        if (not node.left and not node.right):
            self.huffman_table[node.symbol] = newVal
    
        return self.huffman_table
    
    def show_table(self) -> None:
        '''
        Prints the huffman encoding table.
        calls the huffman tree and get_codes function.

        >>> h = Huffman(['a', 'b', 'c', 'd', 'e'], [0.3, 0.25, 0.2, 0.15, 0.1])
        >>> h.show_table()
        +---------+-----------+
        | Symbols | Codewords |
        +---------+-----------+
        |    a    |    00     |
        |    d    |    010    |
        |    e    |    011    |
        |    b    |    10     |
        |    c    |    11     |
        +---------+-----------+        
        '''

        root_node = self.huffman_tree()
        self.__get_codes(root_node)
        l = [list(i) for i in self.huffman_table.items()]
        print(tabulate.tabulate(l, headers=['Symbols', 'Codewords'], tablefmt="pretty", numalign='center'))

    def encode(self, msg: list) -> Tuple[str, Node]:
        '''
        Using the huffman's table encodes a message

        Parameters:
            msg: list
                a list of symbols
        Returns:
            encoded_value: str
                binary string after encoding the message
            root_node: Node
                root_node of the huffman tree. 
        Raises: 
            Assertion error: If message contains invalid symbol

        >>> h = Huffman(['a', 'b', 'c', 'd', 'e'], [0.3, 0.25, 0.2, 0.15, 0.1])
        >>> enc_value, root_node = h.encode(['a', 'b', 'c', 'b', 'c', 'e'])
        >>> print(enc_value)
        b0010111011011
        '''
        assert (i in self.symbols for i in msg)
        root_node = self.huffman_tree()
        self.__get_codes(root_node)
        encoded_val = ''
        for m in msg:
            encoded_val += self.huffman_table[m]
        return encoded_val, self.nodes[0]
        
    
    @staticmethod
    def decode(encoded_value: str, root_node: Node)->str:
        '''
        Decodes the encoded value into a set of symbols

        Parameters:
            encoded_value: str
                encoded value is a string of binary
            root_node: Node
                root node of the huffman tree. Traverses through the node to decode.
        Returns:
            decoded_symbols: str
                the symbols after decoding using the huffman tree. 
        >>> h = Huffman(['a', 'b', 'c', 'd', 'e'], [0.3, 0.25, 0.2, 0.15, 0.1])
        >>> enc_value, root_node = h.encode(['a', 'b', 'c', 'b', 'c', 'e'])
        >>> print(h.decode(enc_value, root_node))
        abcbce
        '''
        tree_head: Node = root_node
        decoded_output = []
        for x in encoded_value:
            if x == '1':
                root_node = root_node.right
            elif x == '0':
                root_node = root_node.left
            try:
                if root_node.left.symbol == None and root_node.right.symbol == None:
                    pass
            except AttributeError:
                decoded_output.append(root_node.symbol)
                root_node = tree_head

        string = ''.join([str(item) for item in decoded_output])
        return string
    
    @staticmethod
    def print_tree(root: Node)-> None:
        '''
        Prints a tree in the terminal given a node

        Parameters:
            root: Node
                pass in a object of class Node prints a tree. 
        
        >>> h = Huffman(['a', 'b', 'c', 'd', 'e'], [0.3, 0.25, 0.2, 0.15, 0.1])
        >>> _, root_node = h.encode(['a', 'b', 'c', 'b', 'c', 'e'])
        >>> h.print_tree(root_node)
        ((a(de))(bc))
            /¯¯¯¯¯¯   ¯¯¯¯¯¯\\
        (a(de))            (bc)
        /¯¯¯ ¯¯¯\       /¯¯¯ ¯¯¯\\
        a    (de)       b       c
                /¯ ¯\\
                d   e
        '''
        def height(root):
            return 1 + max(height(root.left), height(root.right)) if root else -1  
        nlevels = height(root)
        width =  pow(2,nlevels+1)

        q=[(root,0,width,'c')]
        levels=[]

        while(q):
            node,level,x,align= q.pop(0)
            if node:            
                if len(levels)<=level:
                    levels.append([])
            
                levels[level].append([node,level,x,align])
                seg= width//(pow(2,level+1))
                q.append((node.left,level+1,x-seg,'l'))
                q.append((node.right,level+1,x+seg,'r'))

        for i,l in enumerate(levels):
            pre=0
            preline=0
            linestr=''
            pstr=''
            seg= width//(pow(2,i+1))
            for n in l:
                valstr= str(n[0].symbol)
                if n[3]=='r':
                    linestr+=' '*(n[2]-preline-1-seg-seg//2)+ '¯'*(seg +seg//2)+'\\'
                    preline = n[2] 
                if n[3]=='l':
                    linestr+=' '*(n[2]-preline-1)+'/' + '¯'*(seg+seg//2)  
                    preline = n[2] + seg + seg//2
                pstr+=' '*(n[2]-pre-len(valstr))+valstr #correct the potition acording to the number size
                pre = n[2]
            print(linestr)
            print(pstr)   