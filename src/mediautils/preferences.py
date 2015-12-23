"""
Preferences to use in mediautils package
"""

""" Indexing preferences """


# Prefixes for each media type
INDEX_PREFIX = {
                'footage':"MVDC",
                'ctraps':"TRDC",
                'audio':"MSDC",
                }
INDEX_SUFFIX_LENGTH = 5;
INDEX_DATETIME = '%Y%m%d%H%M%S'