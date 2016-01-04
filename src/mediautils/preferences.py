"""
Preferences to use in mediautils package
"""

import os

""" Indexing preferences """
# Prefixes for each media type
INDEX_PREFIX = {
                'footage':"MVDC",
                'ctraps':"TRDC",
                'audio':"MSDC",
                }

INDEX_SUFFIX_LENGTH = 5;
INDEX_DATETIME_FORMAT = '%Y%m%d%H%M%S'


""" Files Storage preferences """
# root directory of media database
MEDIA_DB_ROOT = r'G:\cariama\mediadb' # abs path to media root directory
MEDIA_DB_QUARANTINE_ROOT = os.path.join(MEDIA_DB_ROOT, r'quarantine') # path to quarantine root directory