#!/usr/bin/env python
"""
This module gathers functions for generating and parsing indexes
of the media file objects, from the FDMGM module
This module operates based on the package's preferences

Name:        CARIAMA Indexing System Module
Package:     CARIAMA Media Archive Utilities
"""
import re, time
from datetime import datetime
from preferences import *
from re import IGNORECASE
from mediautils.preferences import INDEX_DATETIME_FORMAT, INDEX_PREFIX

__author__ = "Pedro Correia de Siracusa"
__copyright__ = "Copyright 2015, CARIAMA project"
__credits__ = ["Pedro de Siracusa"]

__licence__ = "Still not defined"
__version__ = "0.1"
__maintainer__ = "Pedro de Siracusa"
__email__ = "pedrosiracusa@gmail.com"
__status__ = "Development"


def getPrefix(mediaType):
    ''' Gets prefix for media type based on the preferences module '''
    try:
        return INDEX_PREFIX[mediaType]
    
    except KeyError:
        raise ValueError("Unknown media type: %s" %mediaType)

def genIndex(prefix, timestamp, suffixNum):
    ''' 
    Generates index based on:
    @param prefix: String prefix to use
    @param timestamp: Datetime in timestamp format
    @param suffixNum: Numeric suffix
    '''               
    indx = prefix + \
            datetime.fromtimestamp(timestamp).strftime(INDEX_DATETIME_FORMAT) + \
            numberFormatToString(suffixNum, length=INDEX_SUFFIX_LENGTH, strict=False)
            
    if not parseIndex(indx):
        raise ValueError("Could not parse generated index")
    
    return indx
    

        

def numberFormatToString(number, length=4, strict=True):
    """ 
    Formats number input to a n-lenghted string
    @param number: Int Number to be formatted to string
    @param length: Length of the string with leading zeroes
    @param strict: If strict, number must fit on the string. If not strict, leading digits are discarded
    """
    
    numString=str(number) 
    if type(number) is not int:
        raise TypeError("Number must be int")
    if length<1:
        return None  
    if number<0:
        raise ValueError("Number must be positive")
    if (number>=10**length):
        if strict:
            raise ValueError("Strict mode: Number must be equal to or smaller than %s" %((10**length)-1))    
        else: 
            return numString[-length:]
        
    while len(numString)<length:
        numString="0"+numString
        
    return numString



def parseIndex(index, parseExp = INDEX_PARSING_EXPRESSION):
    """
    Uses regular expressions to validate the input file's index
    This function does not raise any exceptions
    @param index: Index string to be parsed
    @param parseExp: Regular expression to be matched
    @return: True if input index is valid
    @return: False if input index is not valid
    """
    try:
        pIdx = re.match(parseExp, index).groupdict()
        assert(pIdx['pref'] in INDEX_PREFIX.values())
        idxDate=time.strptime(pIdx['date'], INDEX_DATETIME_FORMAT)

        return{
                'pref': pIdx['pref'], 
                'datestring': pIdx['date'],
                'suff': pIdx['suff'],  
                'datets': time.mktime(idxDate), 
                'mediatype' : [key for key, value in INDEX_PREFIX.items() if value==pIdx['pref']],         
               }
        
    except Exception: return False
    
def indexToDate(indx):
    """
    Parses index datestring to timestamp 
    @param indx: Index to which date must be parsed and extracted
    @return: Timestamp from parsed date
    @raise ImportParsingError: if input index does not parse
    """
    parsedIndx = parseIndex(indx)
    if parsedIndx:
        return time.mktime(time.strptime(parsedIndx['datestring'], INDEX_DATETIME_FORMAT))
    else:
        raise IndexParsingError("Could not parse input index: \'%s\'"%indx)
        

class FileIndexingError(Exception):
    pass

class IndexParsingError(Exception):
    pass
    
def main():
    pass
        
if __name__=='__main__':
    main()