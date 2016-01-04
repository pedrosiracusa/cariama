"""
Preferences to use in mediautils package
"""

import os
from datetime import datetime

""" Indexing preferences """
# Prefixes for each media type
INDEX_PREFIX = {
                'footage':"MVDC",
                'ctraps':"TRDC",
                'audio':"MSDC",
                }

INDEX_SUFFIX_LENGTH = 5;
INDEX_DATETIME_FORMAT = '%Y%m%d%H%M%S'


""" Files Storage and importing preferences """
# root directory of media database
MEDIA_DB_ROOT = r'G:\cariama\mediadb' # abs path to media root directory
MEDIA_DB_QUARANTINE_ROOT = os.path.join(MEDIA_DB_ROOT, r'quarantine') # path to quarantine root directory
IMPORTING_ORGANIZE_BY = { # available organizational methods
                         'date%Y%m': lambda dstRootPath,f:os.path.join(                                               
                                        dstRootPath,
                                        datetime.fromtimestamp(f.getDate()['mtime']).strftime('%Y'),
                                        datetime.fromtimestamp(f.getDate()['mtime']).strftime('%m')                           
                                        ),
                         
                         'date%Y%b': lambda dstRootPath,f:os.path.join(                                               
                                        dstRootPath,
                                        datetime.fromtimestamp(f.getDate()['mtime']).strftime('%Y'),
                                        datetime.fromtimestamp(f.getDate()['mtime']).strftime('%b')                           
                                        ),
                         
                         'date%Y%B': lambda dstRootPath,f:os.path.join(                                               
                                        dstRootPath,
                                        datetime.fromtimestamp(f.getDate()['mtime']).strftime('%Y'),
                                        datetime.fromtimestamp(f.getDate()['mtime']).strftime('%B')                           
                                        ),
                    }


def main():
    pass

if __name__=="__main__":
    main()
    
    