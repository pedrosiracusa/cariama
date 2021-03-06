"""
Preferences to use in mediautils package
"""

import os, time
from datetime import datetime


""" Indexing System Preferences """
# Prefixes for each media type
INDEX_PREFIX = {
                'footage':"MVDC",
                'ctraps':"TRDC",
                'audio':"MSDC",
                }

INDEX_SUFFIX_LENGTH = 5;
INDEX_DATETIME_FORMAT = '%Y%m%d%H%M%S'
INDEX_DATETIME_LENGTH = lambda dtformat=INDEX_DATETIME_FORMAT: len( time.strftime(dtformat, time.localtime(time.clock())) ) 
INDEX_PARSING_EXPRESSION = '(?P<pref>[A-Za-z]+)(?P<date>\d{'+str(INDEX_DATETIME_LENGTH())+'})(?P<suff>\d{'+str(INDEX_SUFFIX_LENGTH)+'}$)'


""" Files Storage and importing preferences """
# root directory of media database
MEDIA_DB_ROOT = r'G:\cariama\mediadb' # abs path to media root directory
MEDIA_DB_QUARANTINE_ROOT = os.path.join(MEDIA_DB_ROOT, r'quarantine') # path to quarantine root directory
IMPORTING_ORGANIZE_BY = { # available organizational methods
                         'PREFIX/date%Y%m': lambda dstRootPath,f:os.path.join(                                               
                                        dstRootPath,
                                        INDEX_PREFIX[f.getMediaType()],
                                        datetime.fromtimestamp(f.getDatetime()).strftime('%Y'),
                                        datetime.fromtimestamp(f.getDatetime()).strftime('%m')                           
                                        ),
                         
                         'date%Y%b': lambda dstRootPath,f:os.path.join(                                               
                                        dstRootPath,
                                        datetime.fromtimestamp(f.getDatetime()).strftime('%Y'),
                                        datetime.fromtimestamp(f.getDatetime()).strftime('%b')                           
                                        ),
                         
                         'date%Y%B': lambda dstRootPath,f:os.path.join(                                               
                                        dstRootPath,
                                        datetime.fromtimestamp(f.getDatetime()).strftime('%Y'),
                                        datetime.fromtimestamp(f.getDatetime()).strftime('%B')                           
                                        ),
                    }

MEDIA_DB_DIR_STRUCTURE = 'PREFIX/date%Y%m' # Chose media db directories structure


def main():
    print(INDEX_DATETIME_LENGTH())

if __name__=="__main__":
    main()
    
    