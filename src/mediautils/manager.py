#!/usr/bin/env python
"""
MediaUtils Package Management Module

Name:        Package Management Module (management)
Package:     CARIAMA Media Archive Utilities
"""

import tkinter as tk
from tkinter import filedialog

import argparse
from clint.textui import prompt, validators, puts, colored, progress, indent

from preferences import INDEX_PREFIX, MEDIA_DB_QUARANTINE_ROOT, MEDIA_DB_ROOT, MEDIA_DB_DIR_STRUCTURE
import fdmgm
from fdmgm import File, Directory
from fdmgm import importFile
from fdmgm import FileImportingError, DirectoryIntegrityError

from indexing import ParserError, FileIndexingError

import os, sys, time, logging
from argparse import Namespace


""" Setup logger """

handler = logging.FileHandler('log.log')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('\n%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
handler.setFormatter(formatter)



""" Functions """

def getFilesFromDialog(args):
    """ Opens file dialog GUI for file or directory
    @return: a list of selected files
    """
    root = tk.Tk()
    root.withdraw()
    if args.file_select:
        return [File(f) for f in filedialog.askopenfilenames()]
    elif args.dir_select:
        try:
            return Directory(filedialog.askdirectory()).getFiles()
        except NotADirectoryError:
            return []
    else:
        raise ValueError("Invalid mode")
    

class Import():
    def __init__(self, args, parser):   
        if args.quarantine:
            if args.mediatype is None:
                parser.error("quarantine importing mode requires -t/--mediatype to be set")
            if args.mediatype not in INDEX_PREFIX.keys():
                parser.error("invalid media type: %s"%args.mediatype)
            if not (args.dir_select or args.file_select):
                parser.error("must specify -d or -f for directory or file selector")
            self.__import_to_quarantine(args)
            
        elif args.database: 
            self.__import_to_database(args)
        elif args.path:
            if args.index and not args.mediatype:
                parser.error("custom path importing mode can only apply index if -t/--mediatype is set")
            self.__import_to_path(args)
            
    def __del__(self):
        with indent(4, quote=">>"): puts(colored.cyan("Done"))
    
    def __import_files(self, fList, destPath, organizeBy=None, copy=True, indexing=False):
        """ Base function for importing files """
        # set logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)    
        
        # importing routine
        with indent(3, quote='>>'): puts(colored.cyan("Importing Files to %s"%destPath))  
        with progress.Bar(expected_size=len(fList)) as bar:
                    val=0
                    for f in fList:
                        val +=1
                        try:                        
                            with indent(5): puts(colored.green("Importing file %s"%f.getPath()))   
                            bar.show(val-1)                         
                            impf = importFile(f, destPath, organizeBy=organizeBy, indexing=indexing)
                            logger.info("Imported file %s successfully into %s"%(f.getPath(),impf.getPath()))
                        
                        except FileImportingError as e:
                            with indent(5): puts(colored.red("%s"%e))
                            logger.error("Error importing file", exc_info=True)
                            
                        finally:                      
                            bar.show(val)
       
    def __import_to_quarantine(self, args):
        """ 
        Opens a file selector and lets user pick up files to be imported to quarantine 
        @param param: 
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        # file selector dialog
        flist = getFilesFromDialog(args)
        
        # sets media type
        for f in flist:
            f.setMediaType(args.mediatype)
        
        # importing routine
        importPath = os.path.join(MEDIA_DB_QUARANTINE_ROOT, args.quarantine)
        self.__import_files(flist, importPath, organizeBy=None, copy=True, indexing=args.index)
        
        # finalization
        return
        
    def __import_to_database(self, args):
        """ Imports file to media database from the quarantine. Checks its integrity first """
        # Verify quarantine before importing files
        setFix=False
        while True:
            try: # tries to pass integrity check
                quarantine = Directory(MEDIA_DB_QUARANTINE_ROOT)
                quarantine.checkIntegrity(fix=setFix)
                break
                
            # prints out the issues detected on quarantine    
            except DirectoryIntegrityError as e: 
                with indent(4, quote=">>"):
                    puts("The following issues were detected on the quarantine:")
                print("\n")
                for issue in e.issues:
                    with indent(8): puts(colored.red("[%s]\n %s for file %s\n"%(issue[0], issue[1][1], os.path.relpath(issue[1][0], quarantine.getPath()))) )
                
                # try to fix issues?
                setFix = prompt.query("Do you want me to try fixing them? [y/n]", validators=[validators.OptionValidator(["Y", "y", "N", "n"], "type y (yes) or n (no)")])
                if setFix=='y' or setFix=="Y":
                    setFix=True
                    print("trying to fix\n\n\n")
                    pass
                # do not try to fix issues. quit importing routine
                else:
                    with indent(3, quote=">>"): puts("Could not fix the issues. Now quitting...")
                    sys.exit()                     
        
        
        # if quarantine is all set, start importing routine
        flist = [f for f in quarantine.getFiles(recursive=True)]
        self.__import_files(flist, MEDIA_DB_ROOT, organizeBy=MEDIA_DB_DIR_STRUCTURE, copy=True, indexing=False)
        
        # finalization
        return
  
    def __import_to_path(self, args):
        """ Opens a file selector and lets user pick up files to be imported to custom path """
        # file selector dialog
        flist = getFilesFromDialog(args)
            
        # sets media type
        for f in flist:
            f.setMediaType(args.mediatype)
            
        # importing routine
        self.__import_files(flist, args.path, organizeBy=None, copy=True, indexing=args.index)
        

class Datetime():
    def __init__(self, args, parser):
        if args.add:
            with indent(4, quote=">>"): puts(colored.cyan("Entering datetime add mode..."))
            
            self.__add(args)
        if args.fix:
            with indent(4, quote=">>"):puts(colored.cyan("Entering datetime fixing mode..."))
            self.__fix(args)
            
    def __del__(self):
        with indent(4, quote=">>"): puts(colored.cyan("Done"))
    
    def __add(self, args):
        """ Opens a file selector and adds an amount of seconds for each """
        # file selector dialog
        flist = getFilesFromDialog(args)
        
        # add seconds
        numOfSecs=eval(args.add)
        for f in flist:
            f.setDatetime((f.getDatetime()+numOfSecs))
            
    def __fix(self, args):
        """ Opens a file selector and tries to fix datetime for each file """ 
        # file selector dialog
        flist = getFilesFromDialog(args)
        
        # try to fix
        for f in flist:
            try:
                f.setDatetime(fromIndex=True)
                with indent(8):puts( colored.green("Fixed datetime from %s"%(f.getName())) )
            except ValueError:
                with indent(8): puts( colored.red("Could not fix datetime from %s"%f.getName()) )

class SetIndex():
    def __init__(self, args, parser):
        self.__update_index(args)
        
    def __del__(self):
        pass
    
    def __update_index(self, args):
        # file selector dialog
        flist= getFilesFromDialog(args)
        
        # update files
        for f in flist:
            try:
                f.setDatetime(fromIndex=True)
                f.setMediaType(f.getMediaType())
                f.setIndex()
            except ValueError as e:
                with indent(4): puts(colored.red("Could not update index from %s: %s"%(f.getName(),e)))
            except FileIndexingError as e:
                with indent(4): puts(colored.red("Could not update index from %s: %s"%(f.getName(), e.strerror)))
            

def main():
    
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', help='additional help')  
    
    # Import subcommand
    parser_import = subparsers.add_parser('import',  help='import files')    
    parser_import_mode = parser_import.add_mutually_exclusive_group(required=True)
    parser_import_fselector = parser_import.add_mutually_exclusive_group()
    parser_import_mode.add_argument('--quarantine', nargs='?', const='.', help="Import files to system quarantine root, or an optional subdir specified by [SUBPATH]. Specify media type with -t/--mtype and selector assistant for file (-f) or directory (-d)", metavar="SUBPATH")
    parser_import_mode.add_argument('--database', help="Import files from quarantine to media database", action="store_true")
    parser_import_mode.add_argument('--path', help="Import files to a custom path. Specify whether to apply indexation with -i/--index and choose selector assistant for file (-f) or directory (-d). If indexing, must specify media type -t/--mediatype")
    parser_import.add_argument('-t', '--mediatype', help='Specify media type')
    parser_import.add_argument('-i', '--index', help="Apply indexing to files on importing", action="store_true")
    parser_import_fselector.add_argument('-d', help="Use directory selector assistant", action="store_true", dest="dir_select")
    parser_import_fselector.add_argument('-f', help="Use file selector assistant", action="store_true", dest="file_select")
    parser_import.set_defaults(func=Import, parser_name="parser_import") 
    
       
    # Datetime subcommand
    parser_datetime = subparsers.add_parser('datetime', help='file datetime operations')
    parser_datetime_mode = parser_datetime.add_mutually_exclusive_group(required=True)
    parser_datetime_fselector = parser_datetime.add_mutually_exclusive_group(required=True)
    parser_datetime_mode.add_argument('--add', help="Add an ammount of seconds to file datetime", metavar="SECS")
    parser_datetime_mode.add_argument('--fix', help="Try to fix file datetime based on index parsing", action="store_true")
    parser_datetime_fselector.add_argument('-d', help="Use directory selector assistant", action="store_true", dest="dir_select")
    parser_datetime_fselector.add_argument('-f', help="Use file selector assistant", action="store_true", dest="file_select")
    parser_datetime.set_defaults(func=Datetime, parser_name="parser_datetime")
    
    # Setindex subcommand
    parser_setindex = subparsers.add_parser('setindex', help="file indexation")
    parser_setindex_fselector = parser_setindex.add_mutually_exclusive_group(required=True)
    parser_setindex.add_argument('-u','--update', help="try to parse datetime and media type from previous index and update it", action="store_true")
    parser_setindex_fselector.add_argument('-d', help="use directory selector assistant", action="store_true", dest="dir_select")
    parser_setindex_fselector.add_argument('-f', help="use file selector assistant", action="store_true", dest="file_select")
    parser_setindex.set_defaults(func=SetIndex, parser_name="parser_setindex")
        
    # arguments parsing
    args = parser.parse_args()  

    # call functions
    args.func(args, eval(args.parser_name))
      
if __name__=='__main__':
    main()