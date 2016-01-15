#!/usr/bin/env python
"""
This module gathers functions for generating and parsing indexes
of the media file objects, from the FDMGM module
This module operates based on the package's preferences

Name:        CARIAMA Indexing System Module
Package:     CARIAMA Media Archive Utilities

Next: Implement index parser class?
"""
import re, time
from datetime import datetime
from preferences import INDEX_SUFFIX_LENGTH, INDEX_PARSING_EXPRESSION, INDEX_DATETIME_FORMAT, INDEX_PREFIX
from parser import ParserError

__author__ = "Pedro Correia de Siracusa"
__copyright__ = "Copyright 2015, CARIAMA project"
__credits__ = ["Pedro de Siracusa"]

__licence__ = "Still not defined"
__version__ = "0.1"
__maintainer__ = "Pedro de Siracusa"
__email__ = "pedrosiracusa@gmail.com"
__status__ = "Development"


def getPrefix(mediaType):
    """ 
    Gets prefix for media type based on the preferences module
    @param mediaType: media type to prefix
    @return: prefix corresponding to media type
    @raise ValueError: if input media type is invalid 
    """
    try:
        return INDEX_PREFIX[mediaType]
    
    except KeyError:
        raise ValueError("Unknown media type: %s" %mediaType)

def genIndex(prefix, timestamp, suffixNum):
    ''' 
    @TODO: test if timestamp and prefix are not valid
    Generates index based on:
    @param prefix: String prefix to use
    @param timestamp: Datetime in timestamp format
    @param suffixNum: Numeric suffix
    @return: index string
    @raise ValuError: if generated index was not valid
    '''   
    try:            
        indx = prefix + \
                datetime.fromtimestamp(timestamp).strftime(INDEX_DATETIME_FORMAT) + \
                numberFormatToString(suffixNum, length=INDEX_SUFFIX_LENGTH, strict=False)
        parseIndex(indx)
         
    
    except (AssertionError, ValueError, OSError):
        raise ParserError(1000)  
         
    
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

def parseIndex(index, parseExp = INDEX_PARSING_EXPRESSION, parseDtFormat = INDEX_DATETIME_FORMAT, ignoreErrors=False):
    """
    Uses regular expressions to validate the input file's index
    This function does not raise any exceptions
    @param index: Index string to be parsed
    @param parseExp: Regular expression to be matched
    @return: True if input index is valid
    @return: False if input index is not valid
    """
    res={}
    try:
        pIdx = re.match(parseExp, index).groupdict()
        if 'pref' in pIdx.keys():
            res['pref']=pIdx['pref']
            if not pIdx['pref'] in INDEX_PREFIX.values():
                if not ignoreErrors: raise ParserError(1)  
            else:
                res['mediatype']=[key for key, value in INDEX_PREFIX.items() if value==pIdx['pref']][0]    
        
        if 'date' in pIdx.keys():
            try:
                res['datestring'] = pIdx['date']                
                idxDate=time.strptime(pIdx['date'], parseDtFormat)
                res['datets'] = time.mktime(idxDate)                
            except ValueError:
                if not ignoreErrors: raise ParserError(2, "Invalid datestring: %s"%pIdx['date'])

        if 'suff' in pIdx.keys():
            res['suff']=pIdx['suff']

        
        return res
    
    except AttributeError:
        raise ParserError(0)
    
            
        
class FileIndexingError(Exception):
    """ 
        Accepts 3 positional arguments: ([strerror, filename [,index]]) 
    """
    def __init__(self, *args):
        self.strerror=None,
        self.filename=None,
        self.index = None
        try:
            self.strerror = args[0]
            self.filename = args[1]
            self.index = args[2]
        except IndexError:
            pass
        
    def __str__(self):
        msgstr = "%s: %s"%(self.strerror, self.filename)
        if self.index is not None:
            msgstr+="; index attempted: %s"%self.index
        return (msgstr)


class ParserError(Exception):
    err = {
           0: ("EMTCH", "RegEx Match Error"), # String did not match expression"
           1: ("EPREM", "Prefix Error"), # Prefix does not correspond to any valid media type"
           2: ("EDATE", "Datestring Error"), # Invalid date
           1000:("EUNKN", "Unknown Error")
           }    
    
    def __init__(self, code, msg=None, *args, **kwargs):
        self.code=code
        self.msg=msg
        
    def __str__(self):
        
        if self.msg==None:
            return "[err%s] %s"%(self.err[self.code][0], self.err[self.code][1])
        else:
            return "[err%s] %s"%(self.err[self.code][0], self.msg)
    
    
def main():
    idx="a123prefix2014121215"
    print(parseIndex(idx, "(?P<pref>[A-Za-z]+(?P<date>\d.*))", parseDtFormat="%Y%m%d%H", ignoreErrors=True))
        
if __name__=='__main__':
    main()