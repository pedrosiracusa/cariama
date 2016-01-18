#!/usr/bin/env python
"""
Base module that provides basic classes and functions for representing 
and managing multimedia files and directories in which they are stored

File and Directory classes are WRAPPERS for files and directories on the
os filesystem, and therefore their instantiation will not CREATE new files 
and directories automatically. The File class does not edit file contents

File and Directory classes have two basic attributes: a path (reference to 
underlying file) and an associated media type

Name:        Files and Directories Management Module (FDMGM)
Package:     CARIAMA Media Archive Utilities
"""

import os, time, stat, shutil, errno
import datetime
import indexing as indx
import filecmp
import re
from preferences import INDEX_PREFIX, IMPORTING_ORGANIZE_BY, INDEX_DATETIME_FORMAT, INDEX_DATETIME_LENGTH

import traceback

__author__ = "Pedro Correia de Siracusa"
__copyright__ = "Copyright 2015, CARIAMA project"
__credits__ = ["Pedro de Siracusa"]

__licence__ = "Still not defined"
__version__ = "0.1"
__maintainer__ = "Pedro de Siracusa"
__email__ = "pedrosiracusa@gmail.com"
__status__ = "Development"

class File:
    """ 
    Wrapper class for media files 
    
    Args:
        filePath(str): Path for a valid media file.
        mediatype(str, optional): Media file type. Valid types are listed on preferences module. Defaults to None
    
    Attributes:
        private filePath: The path to file on filesystem
        private mediatype: The media type for this file
    """
    def __init__(self, filePath, mediaType=None):
        self.__filePath = filePath
        try:
            if not os.path.isfile(self.__filePath):
                raise FileNotFoundError("File instance could not be linked to input file: file does not exist")
        except TypeError:
                raise FileNotFoundError("File instance could not be linked to None input file")  
        
        self.__mediaType = mediaType
 
    def exists(self):
        """ 
        Checks whether input file path exists. Defaults to instance's filePath attribute 
        
        Returns:
            True if file exists in filesystem, and False otherwise
        """
        filePath = self.__filePath
            
        try:
            if os.path.isfile(filePath):
                return True
            else:
                return False
         
        except TypeError:
            return False       
    
    def getPath(self):
        """ Retrieves file full path
        
        Returns:
            File path(path)
        """
        return(self.__filePath)
    
    def getName(self):
        """ Retrieves file basename, without extension
        
        Returns:
            File name(str)
        """
        return(os.path.splitext(os.path.basename(self.__filePath))[0])
    
    def getExt(self):
        """ Retrieves file extension
        
        Returns:
            File extension(str)
        """
        return(os.path.splitext(self.__filePath)[1])
    
    def getDir(self):
        """ 
        Retrieves the dir in which the file is located 
        
        Returns:
            File directory(path)
        """
        return(os.path.dirname(self.__filePath))
    
    def getDatetime(self, mode="mtime", format=False, fromIndex=False, indexRePattern=None, indexDtFormat=INDEX_DATETIME_FORMAT):
        """
        TODO: change format default to None
        Returns a dict with creation, modification and access dates.
            
        Args:
            mode (str): Specify which mode to use from ["mtime", "ctime", "atime"]. Defaults to "mtime".
            format (str, optional): Pattern to format output datetime. If None, timestamp is returned.  Defaults to None.
            fromIndex (bool, optional): If true, datetime is returned from parsing file's index. Otherwise datetime is returned from file's metadata. Defaults to False.
            indexRePattern(str, optional): Regular Expression pattern to be used to match against parser. Usually do not touch. Default defined on method body.
            indexDtFormat(str, optional): Datetime format to be parsed from index. Default set on preferences module.

        Returns:
            A datetime(str) or a timestamp(float).

        Raises:
            ValueError: if 'mode' is not valid.
            ParserError: if 'fromIndex == True and index parsing fails.
        """
        if not fromIndex:
            if mode=="mtime":
                dt = os.path.getmtime(self.__filePath)
            elif mode=="atime":
                dt = os.path.getatime(self.__filePath)
            elif mode=="ctime":
                dt = os.path.getctime(self.__filePath)
            else:
                raise ValueError("Invalid mode: %s"%mode)
            
        else:
            indxToParse = self.getName()
            # try to parse and raise parser error in case it fails
            if indexRePattern is None:
                indexRePattern = '(?P<pref>[A-Za-z]+)(?P<date>\d{'+str(INDEX_DATETIME_LENGTH(indexDtFormat))+'}).*' # default index pattern                             
            dt = indx.parseIndex(indxToParse, parseExp=indexRePattern, parseDtFormat=indexDtFormat, ignoreErrors=True)['datets']
            # index parsed successfully
            
        
        # return timestamp or formatted
        if format:
            return datetime.datetime.fromtimestamp(dt).strftime(format)
        return dt
        
    def getSize(self):
        """ Retrieves the size of the file, in bytes 
        
        Returns:
            File size in bytes (int)
        """
        if self.exists():
            return (os.path.getsize(self.__filePath))
        else:
            raise FileNotFoundError("[mediautils.getSize] File not found: %r" %(self.__filePath))
    
    def getMediaType(self):
        """ Retrieves file media type
        
        Note:
            This method tries to get media type from its private attribute,
            and if it is not set, tries to parse it from index prefix, in case
            file is already indexed
        
        Returns:
            mediaType(str)    
        """
        mtype = self.__mediaType
        if mtype is None:
            try: 
                mtype = indx.parseIndex(self.getName(), 
                                "(?P<pref>[A-Za-z]+).*", 
                                ignoreErrors=True)['mediatype']
            except KeyError:
                pass
            
        return mtype
    
    def setMediaType(self, mediaType):
        """
            Sets file media type
            On next implementations use file headers to define file type
            
        Args:
            mediatype(str): Media type to be set to file. Valid types are defined on preferences module.
        
        Raises ValueError:
            If input media type is invalid
        """     
        if mediaType not in INDEX_PREFIX.keys() and mediaType is not None:
            raise ValueError("Invalid media type: %s"%mediaType)
        
        self.__mediaType=mediaType
            
    def setName(self, name):
        """ 
        Renames the file, keeping the path and extension
        
        Args:
            name(str): New file name 
            
        Raises:
            FileExistsError: If another file already exists with the same name
        """
        fileDir = os.path.dirname(self.__filePath)
        fileExt = os.path.splitext(self.__filePath)[1]
        newFilePath = os.path.join(fileDir, name+fileExt)
        if os.path.isfile(newFilePath):
            raise FileExistsError("File %r already exists" %(newFilePath))
        
        os.rename(self.__filePath, newFilePath)
        self.__filePath = newFilePath
        
    def setIndex(self, force=False):
        """ Sets file index based on indexing rules module 
        
        Args:
            force(bool, optional): If True, an already indexed file may be re-indexed. Otherwise, re-indexing 
            does not occurr. Defaults to False

        Raises:
            FileIndexingError: If method fails to set index to file
        """
        # only set index if file is not already indexed
        try: # check if name is a valid index
            indx.parseIndex(self.getName())
            if not force:
                raise indx.FileIndexingError("Could not set index to file (file is already indexed)",self.__filePath, self.getName())
            else:
                self.setDatetime(fromIndex=True)
        
        except indx.ParserError: # if file was not already indexed, do it
            try:
                indxPref = indx.getPrefix(self.getMediaType())
                indxDate = self.getDatetime()
                indxSuff = self.getSize()
                index = indx.genIndex(indxPref, indxDate, indxSuff)
                self.setName(index)
            
            except ValueError as e:
                raise indx.FileIndexingError("Could not format index", self.__filePath, None)
            
            except FileExistsError as e:
                raise indx.FileIndexingError("Same index already exists", self.__filePath, index)
                    
    def setDatetime(self, timestamp=None, mode="am", fromIndex=False, indexPattern=None, datetimeFormat=INDEX_DATETIME_FORMAT):
        """ Updates file modification and/or access date
        
        Args:
            timestamp(float): Timestamp to be used to update datetime. Not required if fromIndex is True
            mode(str): Which type of date to use (a:atime; m:mtime; am:both)
            fromIndex(bool): If True, tries to parse datetime from index and raises error if it fails. Defaults to False
            indexPattern(str): Custom regex for parsing index. Default is defined on method's body
            datetimeFormat(str): The datetime format against which to parse index. Default defined on preferences
            
        Raises:
            ValueError: If no valid datestring can be parsed from index
            ValueError: If input mode is invalid
            TypeError: If not in fromIndex mode and timestamp is not provided
        """
        if fromIndex:
            if indexPattern is None:
                regex = '(?P<pref>[A-Za-z]+)(?P<date>\d{'+str(INDEX_DATETIME_LENGTH(datetimeFormat))+'}).*' # default index pattern                
            # Date parsing
            try: 
                timestamp = indx.parseIndex(self.getName(), regex, parseDtFormat=datetimeFormat, ignoreErrors=True)['datets']              
                                              
            except (KeyError, indx.ParserError): # parsing failed
                raise ValueError("No valid datestring was found on input index")
        
        # not in fromIndex mode    
        elif timestamp is None:
            raise TypeError( "setDatetime() missing required argument: timestamp")
            
        # Setting datetime routine
        if mode=='a':
            os.utime(self.__filePath, (timestamp, os.path.getmtime(self.__filePath)))
        elif mode=='m':
            os.utime(self.__filePath, (os.path.getatime(self.__filePath), timestamp))
        elif mode=='am':
            os.utime(self.__filePath, (timestamp, timestamp))
        else:
            raise ValueError("Invalid mode")
        
    def unlink(self):
        """ Unlinks this File instance to file in directory, setting path attribute to None """
        self.__filePath=None
         
    def copyTo(self, destPath, bufferSize=10485760, preserveDate=True, strict=True):
        """Copies file from current path to destination. Checks if the same file or 
        another file with the same name already exists on destination before entering the routine
        
        Args:
            destPath(str): Full path to destination, including file name and extension
            bufferSize(int, optional): Buffer size to use during copying. Defaults to 10MB
            preserveDate(bool, optional): If true preserves the original file date. Defaults to True
            strict(bool, optional): If False, the same file may be copied with a different name. Defaults to True
        
        Returns:
            A reference to an instance of a new File object
            
        Raises:
            FileExistsError: If a file with the same name already exists on destination
        """
        # Make sure target directory exists; create it if necessary
        destDir, destFName = os.path.split(destPath) 
        if not os.path.isdir(destDir):
            os.makedirs(destDir)
        
        # Check if destination file already exists in directory; Abort copying if positive
        fList = [f for f in os.listdir(destDir) if os.path.isfile(os.path.join(destDir, f))]
        for f in fList:
            # first line check if files contents are the same (regardless of path) and second checks if file path already exists
            if  (filecmp.cmp(self.__filePath, os.path.join(destDir, f)) and strict) or \
                (destPath==os.path.join(destDir, f)):
                    raise FileExistsError(errno.EEXIST,"File already exists", os.path.join(destDir, f))
                
        # Optimize buffer for small files
        bufferSize = min(bufferSize, os.path.getsize(self.__filePath))
        if bufferSize==0:
            bufferSize=1024  
             
        # Copying routine
        with open(self.__filePath, 'rb') as fsrc:
            with open(destPath, 'wb') as fdst:
                shutil.copyfileobj(fsrc, fdst, bufferSize)
        if(preserveDate):
            shutil.copystat(self.__filePath, destPath)
            
        return File(destPath, mediaType=self.__mediaType)
           
    def moveTo(self, destPath, strict=True):
        """
        Moves file from current path to destination. Checks if file already exists 
        on destination before moving. This function does not return a reference to file,
        but simply moves it and changes path attribute
        
        Args:
            destPath(str): Full path to destination, including file name and extension
            strict(bool, optional): If False, the file can be moved to a directory where it already exists, with another name
        
        Raises:
            FileExistsError: If a file with the same name already exists on destination
        """
        # Make sure target directory exists; create it if necessary
        destDir, destFName = os.path.split(destPath) 
        if not os.path.isdir(destDir):
            os.makedirs(destDir)
        
        # Check if destination file already exists in directory; Abort moving if positive
        fList = [f for f in os.listdir(destDir) if os.path.isfile(os.path.join(destDir, f))]
        for f in fList:
            # first line check if files contents are the same (regardless of path) and second checks if file path already exists
            if  (filecmp.cmp(self.__filePath, os.path.join(destDir, f)) and strict) or \
                (destPath==os.path.join(destDir, f)):                
                    raise FileExistsError(errno.EEXIST,"File already exists", os.path.join(destDir, f))
  
        # Moving routine
        shutil.move(self.__filePath, destPath)
        
        self.__filePath=destPath
                  
    def delete(self):
        """ Deletes object and file at filesystem
        
        Raises:
            FileNotFoundError: If object references a  non-existent file
         """
        if not self.exists():
            raise FileNotFoundError(errno.ENOENT, "Cannot delete a non-existent file", self.__filePath)
        try:
            os.remove(self.__filePath)
        except PermissionError:
            os.chmod(self.__filePath, stat.S_IWUSR)
            os.remove(self.__filePath)
            
        self.unlink()
          
    def __str__(self):
        return (self.__filePath)
 
    
class Directory:
    """ Wrapper class for directories where media files are stored 
    
    Args:
        dirPath(str): Path for a valid directory.
        mediatype(str, optional): Directory media type. Valid types are listed on preferences module. Defaults to None
    
    Attributes:
        private filePath: The path to directory on filesystem
        private mediatype: The media type for this directory
        
    Raises:
        NotADirectoryError: If filePath is not a valid directory
        """
    def __init__(self, dirPath, mediaType=None):
        self.__dirPath = dirPath
        try:
            if not os.path.isdir(self.__dirPath):
                raise NotADirectoryError(errno.ENOTDIR, "Directory instance could not be linked to non-existent directory", self.__dirPath)
        except TypeError:
            raise NotADirectoryError("Directory instance could not be linked to None input path")
        
        self.__mediaType = mediaType
       
    def exists(self):
        """ Checks whether object directory path exists
            
        Returns:
            True if object path points to an existing directory and False otherwise
        """
        dirPath = self.__dirPath           
        try:
            if os.path.isdir(dirPath):
                return True
            else:
                return False
         
        except TypeError:
            return False   
    
    def getPath(self):
        """ Retrieves object directory path
        
        Returns:
            Directory path (str)
        """
        return self.__dirPath
    
    def getName(self):
        """ Retrieves the directory basename
        
        Returns:
            Directory basename (str)
        """
        return os.path.basename(self.__dirPath)
    
    def getSize(self, recursive=True):
        """ 
        Returns the size of files inside input directory
        
        Args:
            recursive(bool, optional): If True, size of files in all subdirectories are also calculated, otherwise only
            files in current level are considered. Defaults to True
            
        Returns:
            Total size of files in bytes (int)
        
        Raises:
            NotADirectoryError: If object is not linked to a real directory in filesystem
        """
        totalSize=0
        if self.exists():
            if recursive:
                for root, dirs, files in os.walk(self.__dirPath):
                    for f in files:
                        fp = os.path.join(root, f)
                        totalSize+=os.path.getsize(fp)
            
            else: # not recursive
                for file in [f for f in os.listdir(self.__dirPath) if os.path.isfile(os.path.join(self.__dirPath, f))]:
                    totalSize+=os.path.getsize(os.path.join(self.__dirPath,file))
               
        else:
            raise NotADirectoryError(errno.ENOTDIR, "Cannot get size of a non-existing directory", self.__dirPath)
                
        return totalSize
    
    def getMediaType(self):
        """ Retrieves media type from directory
        
        Returns:
            Directory media type (str)
        """
        return self.__mediaType
        
    def getDirs(self, recursive=True):
        """ 
        Gets children directories from object
        
        Args:
            recursive(bool, optional): If True, method works recursively, looking for directory on
            all sublevels. If not, only base level is considered. Defaults to True
        
        Returns:
            Directory objects list (list)
            
        Raises:
            NotADirectoryError: If object path is invalid
        """
        if self.exists():
            if not recursive:
                dirList = [Directory(os.path.join(self.__dirPath, name), mediaType=self.__mediaType) for name in os.listdir(self.__dirPath) if os.path.isdir(os.path.join(self.__dirPath, name))]
            
            else:
                dirList=[]
                for path, dirs, files in os.walk(self.__dirPath):
                    dirList.append(Directory(path, mediaType=self.__mediaType))
                  
                dirList.pop(0) # removes root dir from list generated by walk
                
        else:
            raise NotADirectoryError(errno.ENOTDIR, "Cannot get children from non-existing directory", self.__dirPath)
        
        return dirList
    
    def getFiles(self, recursive=True):
        """ 
        Gets file objects from within directory 
        
        Args:
            recursive(bool, optional): If True, method works recursively, looking for files on
            all sublevels. If not, only base level is considered. Defaults to True
        
        Returns:
            File objects list (list)
            
        Raises:
            NotADirectoryError: If object path is invalid
        """
        if self.exists():
            if not recursive:
                fList = [File(os.path.join(self.__dirPath, name), mediaType=self.__mediaType) for name in os.listdir(self.__dirPath) if os.path.isfile(os.path.join(self.__dirPath, name))]
            
            else:
                fList=[]
                for root, dirs, files in os.walk(self.__dirPath):
                    fList.extend([File(os.path.join(root, name), mediaType=self.__mediaType) for name in files])
        
        else:
            raise NotADirectoryError(errno.ENOTDIR, "Cannot get files from non-existing directory", self.__dirPath)  
            
        return fList
    
    def unlink(self):
        """ Unlinks this Directory instance to directory, setting path attribute to None """
        self.__dirPath=None
    
    def setMediaType(self, mediaType):
        """ Sets object's media type """
        self.__mediaType = mediaType
   
    def checkIntegrity(self, fix=False):
        """ Checks for dir integrity, with the requisites:
            1 - Files dates are equivalent to their indexes
            2 - All files indexes are valid
            @param fix: If set to True, this methods tries to recursively fix the issues
            @raise DirectoryIntegrityError: If any issues is detected, exception is raised, with a list of detected issues
        """
        import sys
        issues=[]
        for f in self.getFiles():
            try:
                indx.parseIndex(f.getName());
                if f.getDatetime()!= f.getDatetime(fromIndex=f.getName()):
                    raise ValueError(f.getPath(), "Wrong datetime") 
                
            except indx.ParserError as e:
                if fix:
                    try:
                        f.setDatetime(fromIndex=True)
                        f.setIndex()
                        if self.checkIntegrity(fix=True):
                            return True
                    except ValueError as e:
                        issues.append( ValueError(f.getPath(), "Index not set" ).with_traceback(e.__traceback__) )
                else:
                    issues.append( ValueError(f.getPath(), "Invalid index").with_traceback(e.__traceback__) )
                    
            except ValueError as e:
                if fix:
                    try:
                        f.setDatetime(fromIndex=True)
                        if self.checkIntegrity(fix=True):
                            return True
                    except ValueError as e:
                        issues.append( ValueError(f.getPath(),"Index not set").with_traceback(e.__traceback__))
                else:
                    issues.append( e.with_traceback(e.__traceback__))
        
        # base case
        if len(issues)==0:
            return True
        
        # raise exception
        if len(issues)>0:
            raise DirectoryIntegrityError(issues)
            
        return
    
    def __str__(self):
        return self.__dirPath
 

def importFile(srcFile, dstRootPath, organizeBy=None, copy=True, indexing=False):
    """
    Imports media file to destination, in filesystem
    This function does not deal with files metadata
    @param srcFile: File object to be imported. File must be of a valid media type
    @param dstRootPath: Root of destination directory 
    @param organizeBy: Files organizational method. Available options are defined in the preferences module. If None(default), all files are imported to root
    @param copy: If true, files are copied instead of being moved. Defaults to True
    @param indexing: If true, files are automatically indexed on importing. Defaults to False  
    @return: Reference to imported file  
    @raise FileImportingError: if importing fails 
    """ 
    try:
        # find out the target directory for file
        if organizeBy is not None: # use some organizational method
            dstDir = IMPORTING_ORGANIZE_BY[organizeBy](dstRootPath,srcFile)            
        else: # import all files to root dir
            dstDir = dstRootPath
            
        # create Directory object (and path in filesystem if it did not exist)
        while True:
            try: 
                dstDir = Directory(dstDir)
            except NotADirectoryError:
                try:
                    os.makedirs(dstDir) 
                except FileNotFoundError:
                    raise OSError(errno.EINVAL, "Could not create directory", dstRootPath)
          
                continue
            break
            
        # if copy file method is chosen
        if copy:
            try:
                rollbackPath = os.path.join(dstDir.getPath(), srcFile.getName()+srcFile.getExt()) # only for purposes of rolling back
                newf = srcFile.copyTo(os.path.join(dstDir.getPath(), srcFile.getName()+srcFile.getExt()))
                if indexing: 
                    newf.setIndex()
                return newf

            except indx.FileIndexingError as e:
                newf.delete() # rollback
                raise FileImportingError(errno.EPERM, "Could not import file(%s)"%e.strerror, srcFile.getPath())
            
            except FileExistsError as e:
                raise FileImportingError(errno.EPERM, "Could not import file(%s)"%e.strerror, e.filename)
            
            except (KeyboardInterrupt, SystemExit) as e:
                File(rollbackPath).delete() # rollback
                raise
        # if move file method is chosen                          
        else:
            try:
                oldPath = srcFile.getPath()
                srcFile.moveTo(os.path.join(dstDir.getPath(), srcFile.getName()+srcFile.getExt()))
                if indexing:
                    srcFile.setIndex()
                return srcFile
            
            except indx.FileIndexingError as e:
                srcFile.moveTo(oldPath) # rollback
                raise FileImportingError(errno.EPERM, "Could not import file(%s)"%e.strerror, srcFile.getPath())
            
            except FileExistsError as e:
                raise FileImportingError(errno.EPERM, "Could not import file(%s)"%e.strerror, e.filename)                 

            except (KeyboardInterrupt, SystemExit) as e:
                srcFile.moveTo(oldPath) # rollback
                raise
            
    except KeyError as e:
        raise e


class DirectoryIntegrityError(Exception):
    def __init__(self, *args):
        self.issues = [(issue.__class__.__name__, issue.args) for issue in args[0]]

class FileImportingError(OSError):
    pass

def main():
    pass

if __name__=='__main__':
    main()
    