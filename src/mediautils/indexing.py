"""
Name:        File Indexing Module
Package:     CARIAMA Media Archive Utilities

Author:      Pedro Correia de Siracusa

"""
from datetime import datetime
from preferences import *
from fdmgm import File


def getPrefix(file):
    ''' Gets prefix for media type based on the preferences module '''
    try:
        return INDEX_PREFIX[file.getMediaType()]
    
    except KeyError:
        raise ValueError("Unknown media type: %s" %file.getMediaType())

def indexFile(file, prefix=None):
    ''' 
    Sets file's index (renames it)
    Gets default prefix from media type
    '''
    dateTime = datetime.fromtimestamp(file.getDate()['mtime'])
    nameTime = dateTime.strftime(INDEX_DATETIME)
    suffix = numberFormatToString(file.getSize(), length = INDEX_SUFFIX_LENGTH, strict=False)
    
    # By default uses auto generated prefix
    if prefix==None:
        try:
            prefix=getPrefix(file)
        except ValueError:
            raise ValueError("Cannot autoprefix unknown media file")
                
    index=prefix+nameTime+suffix
    
    file.setName(index)
  

def numberFormatToString(number, length=4, strict=True):
    """ 
    Formats number input to a n-lenghted string
    @param number: Int Number to be formatted to string
    @param length: Length of the string with leading zeroes
    @param strict: If strict, number must fit on the string. If not strict, only trailing digits are discarded
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
            return numString[:length]
        
    while len(numString)<length:
        numString="0"+numString
        
    return numString



def parseIndex(file):
    """
    Validates the input file's index
    @TODO
    """
    
    pass

def main():
    print(indexFile(File(r'C:\Users\PEDRO\Desktop\videos_sentinelas\copy\TRDC2013092519103201.AVI', 'photo-traps')))

if __name__=='__main__':
    main()