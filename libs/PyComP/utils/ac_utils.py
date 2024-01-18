
def decToBinConversion(no:float, precision: int) -> str:
    '''
    Converts a decimal number to binary accepts fraction as well

    Parameters:
        no: float 
            decimal number can consist fraction part as well
        precision: int
            precision required for the fractinal part returns fractional part to that precision level
    Returns:
        binary: str
            returns the binary conversion of a decimal number with user-defined precision
    
    '''
    binary = ""
    IntegralPart = int(no)
    fractionalPart = no - IntegralPart
    # to convert an integral part to binary equivalent
    while (IntegralPart):
        re = IntegralPart % 2
        binary += str(re)
        IntegralPart //= 2
    binary = binary[:: -1]
    binary += '.'
    # to convert an fractional part to binary equivalent
    while (precision):
        fractionalPart *= 2
        bit = int(fractionalPart)
        if (bit == 1):
            fractionalPart -= bit
            binary += '1'
        else:
            binary += '0'
        precision -= 1
    return binary


def getBinaryFractionValue(binaryFraction):
    '''            
    Compute the binary fraction value using the formula of:
    (2^-1) * 1st bit + (2^-2) * 2nd bit + ...
    
    Parameters:
        binaryFraction: str
            binary string of the fractional part. 
    Returns:
        value: float
            returns the fractional part in decimal

    '''
    value = 0
    power = 1

    # Git the fraction bits after "."
    fraction = binaryFraction.split('.')[1]

    # Compute the formula value
    for i in fraction:
        value += ((2 ** (-power)) * int(i))
        power += 1

    return value

