import os
import datetime

def convert_bytes(num) -> str:
    """
    This function will convert bytes to MB.... GB... etc.

    Parameters:
        x: float
            input floating point number
        max_precision: int
            max binary precision (after the decimal point) to which we should return the bitarray
    Returns:
        file_size: str
            file size to the nearest MB.... GB...        
    >>> convert_bytes(10580)
        10.3 KB
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def epoch_to_datetime(epoch_time):
    '''
    This function converts epoch into datetime

    Parameters:
        epoch_time: int
            time in epoch scale
    Returns:
        date: datetime
            standard date and time of the epoch time.
    >>> epoch_to_datetime(12452687)
        1970-05-25 08:34:47
    '''
    date_conv = datetime.datetime.fromtimestamp(epoch_time)
    return date_conv


def file_size(file_path):
    """
    This function will return the file size.
    
    Parameters:
        file_path: str
            path of the file
    Returns:
        file_size: int
            size of file in bits
    >>> file_size('/Users/jenish/Library/CloudStorage/Dropbox/crypto/ANS/code/ANS/utils/utils.py')
        3305
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return file_info.st_size


def file_name(file_path):
    '''
    This function will return the file name.

    Parameters:
        file_path: str
            path of the file
    Returns:
        file_name: str
            name of the file with extension
    >>> file_name('/Users/jenish/Library/CloudStorage/Dropbox/crypto/ANS/code/ANS/utils/utils.py')
        utils.py
    '''
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
    return file_name


def file_creation(file_path):
    '''
    This function will return the file creation date

    Parameters:
        file_path: str
            path of the file
    Returns:
        file_creation: Datetime
            file creation time in standard format
    >>> file_creation('/Users/jenish/Library/CloudStorage/Dropbox/crypto/ANS/code/ANS/utils/utils.py')
        2023-03-13 23:11:04.054830
    '''
    if os.path.isfile(file_path):
        file_creation = os.path.getctime(file_path)
        file_creation_time = epoch_to_datetime(file_creation)

    return file_creation_time


def file_last_modified(file_path):
    '''
    This function will return the file modified datetime

    Parameters:
        file_path: str
            path of the file
    Returns:
        file_moodified_time: Datetime
            last modified time in standard format
    >>> file_last_modified('/Users/jenish/Library/CloudStorage/Dropbox/crypto/ANS/code/ANS/utils/utils.py')
        2023-03-13 23:11:01.540858
    '''
    if os.path.isfile(file_path):
        file_modif = os.path.getmtime(file_path)
        file_modif_time = epoch_to_datetime(file_modif)

    return file_modif_time


def file_summary(file_path):
    '''
    Compautes the summary of the file. Runs the file util functions.

    Parameters:
        file_path: str
            path of the file
    Returns:
        name, size, creation, modification: Tuple[str, str, datetime, datetime]
    >>> file_summary('/Users/jenish/Library/CloudStorage/Dropbox/crypto/ANS/code/ANS/utils/utils.py')
        ('utils.py', 3305, datetime.datetime(2023, 3, 13, 23, 11, 4, 54830), datetime.datetime(2023, 3, 13, 23, 11, 1, 540858))
    '''
    name = file_name(file_path)
    size = file_size(file_path)
    creation = file_creation(file_path)
    modification = file_last_modified(file_path)
    return name, size, creation, modification