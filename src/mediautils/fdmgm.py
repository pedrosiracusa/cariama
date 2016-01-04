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

import os, stat, shutil
import indexing as indx
import filecmp
from preferences import IMPORTING_ORGANIZE_BY

__author__ = "Pedro Correia de Siracusa"
__copyright__ = "Copyright 2015, CARIAMA project"
__credits__ = ["Pedro de Siracusa"]

__licence__ = "Still not defined"
__version__ = "0.1"
__maintainer__ = "Pedro de Siracusa"
__email__ = "pedrosiracusa@gmail.com"
__status__ = "Development"

class File:
    def __init__(self, filePath, mediaType=None):
        '''
        @param mediatype: Media type. vals: (video-footage, video-trap, photo-trap, audio)
        '''
        self.__filePath = filePath
        try:
            if not os.path.isfile(self.__filePath):
                raise FileNotFoundError("File instance could not be linked to input file: file does not exist")
        except TypeError:
                raise FileNotFoundError("File instance could not be linked to None input file")  
        
        self.__mediaType = mediaType
 
    def exists(self):
        ''' Checks whether input file path exists. Defaults to instance's filePath attribute '''
        filePath = self.__filePath
            
        try:
            if os.path.isfile(filePath):
                return True
            else:
                return False
         
        except TypeError:
            return False       
    
    def getPath(self):
        return(self.__filePath)
    
    def getName(self):
        return(os.path.splitext(os.path.basename(self.__filePath))[0])
    
    def getExt(self):
        return(os.path.splitext(self.__filePath)[1])
    
    def getDir(self):
        return(os.path.dirname(self.__filePath))
    
    def getDate(self):
        ''' Returns a dict with creation, modification and access dates (timestamps)'''
        return ({'mtime':os.path.getmtime(self.__filePath),
                'ctime':os.path.getctime(self.__filePath),
                'atime':os.path.getatime(self.__filePath)
                })
    
    def getSize(self):
        ''' Returns the size of the file, in bytes '''
        if self.exists():
            return (os.path.getsize(self.__filePath))
        else:
            raise FileNotFoundError("[mediautils.getSize] File not found: %r" %(self.__filePath))
    
    def getMediaType(self):
        return(self.__mediaType)
    
    def setMediaType(self, mediaType):
        ''' 
            Defines the type of media based on file's extension
            On next implementations use file headers to define file type
        @param mediatype: Media type. vals: (video-footage, video-trap, photo-trap, audio)
        '''      
        self.__mediaType=mediaType
            
    def setName(self, name):
        ''' 
        Renames the basename of the file, without dir nor extension
        @param name: New name 
        '''
        fileDir = os.path.dirname(self.__filePath)
        fileExt = os.path.splitext(self.__filePath)[1]
        newFilePath = os.path.join(fileDir, name+fileExt)
        if os.path.isfile(newFilePath):
            raise FileExistsError("File %r already exists" %(newFilePath))
        
        os.rename(self.__filePath, newFilePath)
        self.__filePath = newFilePath
        
    def setIndex(self):
        """ Sets file index based on indexing rules module """
        # only set index if file is not already indexed
        if not indx.parseIndex(self.getName()):
            try:
                indxPref = indx.getPrefix(self.__mediaType)
                indxDate = self.getDate()['mtime']
                indxSuff = self.getSize()
                index = indx.genIndex(indxPref, indxDate, indxSuff)
                self.setName(index)
            
            except ValueError as e:
                raise indx.FileIndexingError(e)
            
            except FileExistsError as e:
                raise indx.FileIndexingError(e)
        # do not re-index file
        else:
            raise indx.FileIndexingError("Cannot set index to file %s. File is already indexed!" %(self.__filePath))
             
    def setDate(self, timestamp, mode="am"):
        ''' 
        Sets file modification or access date using input timestamp
        @param timestamp: timestamp to update 
        @param mode: type of date (a:atime; m:mtime; am:both)
        '''
        if mode=='a':
            os.utime(self.__filePath, (timestamp, os.path.getmtime(self.__filePath)))
        elif mode=='m':
            os.utime(self.__filePath, (os.path.getatime(self.__filePath), timestamp))
        elif mode=='am':
            os.utime(self.__filePath, (timestamp, timestamp))
        else:
            raise ValueError("[mediautils.setDate] Invalid mode")
        
    def unlink(self):
        """ Unlinks this File instance to file in directory, setting path attribute to None """
        self.__filePath=None
         
    def copyTo(self, destPath, bufferSize=10485760, preserveDate=True, strict=True):
        ''' 
        Copies file from current path to destination. Checks if file already exists on destination before 
        Optimized for copying large files
        @param destPath: Destination path
        @param bufferSize: Buffer size to use during copying. Default = 10MB
        @param preserveDate: Preserves the original file date. Default = True 
        @param strict: If false, the same file can be copied with a different name
        @return: instance of new file object
        '''
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
                    raise FileExistsError("[mediautils.copyTo] File %r already exists on destination" %(destFName))
                
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
        ''' 
        Moves file from current path to destination. Checks if file already exists on destination before
        @param destPath: Destination path
        @param strict: If false, the same file can be moved with a different name
        @return: instance of new file object
        '''
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
                    raise FileExistsError("[mediautils.copyTo] File %r already exists on destination" %(destFName))
  
        # Moving routine
        shutil.move(self.__filePath, destPath)
        
        self.__filePath=None
        
        return File(destPath, mediaType=self.__mediaType)
          
    def delete(self):
        """ Deletes file object and at filesystem TODO: put a try-catch harness """
        if not self.exists():
            raise FileNotFoundError("Cannot delete a non-existent file")
        try:
            os.remove(self.__filePath)
        except PermissionError:
            os.chmod(self.__filePath, stat.S_IWUSR)
            os.remove(self.__filePath)
            
        self.unlink()
        return None
          
    def __str__(self):
        '''
        Print class string representation
        '''
        return (self.__filePath)
 
    
class Directory:
    """ This class represents database directory where files are stored"""
    def __init__(self, dirPath, mediaType=None):
        self.__dirPath = dirPath
        try:
            if not os.path.isdir(self.__dirPath):
                raise NotADirectoryError("Directory instance could not be linked to input path: directory does not exist")
        except TypeError:
            raise NotADirectoryError("Directory instance could not be linked to None input path")
        
        self.__mediaType = mediaType
       
    def exists(self):
        """ Checks whether input directory path exists. """
        dirPath = self.__dirPath           
        try:
            if os.path.isdir(dirPath):
                return True
            else:
                return False
         
        except TypeError:
            return False   
    
    def getPath(self):
        return self.__dirPath
    
    def getName(self):
        return os.path.basename(self.__dirPath)
    
    def getSize(self, recursive=True):
        """ 
        Returns the size of all files from input directory
        @param recursive: If recursive, size of files in all subdirectories are also calculated 
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
            raise NotADirectoryError("Cannot get size of a non-existing directory")
                
        return totalSize
    
    def getMediaType(self):
        return self.__mediaType
        
    def getDirs(self, recursive=True):
        """ 
        Gets children directories from object (root)
        @param recursive: If recursive, method looks at all levels. If not, only top level is considered
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
            raise NotADirectoryError("Cannot get children from non-existing directory")
        
        return dirList
    
    def getFiles(self, recursive=True):
        """ 
        Gets file objects from within directory 
        @param recursive: If recursive, method looks at all levels. If not, only top level is considered    
        """
        if self.exists():
            if not recursive:
                fList = [File(os.path.join(self.__dirPath, name), mediaType=self.__mediaType) for name in os.listdir(self.__dirPath) if os.path.isfile(os.path.join(self.__dirPath, name))]
            
            else:
                fList=[]
                for root, dirs, files in os.walk(self.__dirPath):
                    fList.extend([File(os.path.join(root, name), mediaType=self.__mediaType) for name in files])
        
        else:
            raise NotADirectoryError("Cannot get files from non-existing directory")  
            
        return fList
    
    def unlink(self):
        """ Unlinks this Directory instance to directory, setting path attribute to None """
        self.__dirPath=None
    
    def setMediaType(self, mediaType):
        """ Sets object's media type """
        self.__mediaType = mediaType
    
    def __str__(self):
        return self.__dirPath
 

def importFile(srcFile, dstRootPath, organizeBy=None, copy=True, indexing=True):
    """
    Imports media file to destination, in filesystem
    This function does not deal with files metadata
    @param srcFile: File object to be imported. File must be of a valid media type
    @param dstRootPath: Root of destination directory 
    @param organizeBy: Files organizational method. Available options are defined in the preferences module. If None(default), all files are imported to root
    @param copy: If true, files are copied instead of being moved. Defaults to True
    @param indexing: If true, files are automatically indexed on importing. Defaults to True  
    @return: Reference to imported file  
    """ 
    try:
        # find out the target directory for file
        if organizeBy is not None: # use some organizational method
            dstDir = IMPORTING_ORGANIZE_BY[organizeBy](dstRootPath,srcFile)            
        else: # import all files to root dir
            dstDir = dstRootPath
            
        # create Directory object (and path in filesystem if it did not exist)
        try: 
            dstDir = Directory(dstRootPath)
        except NotADirectoryError:
            os.makedirs(dstRootPath)
            dstDir = Directory(dstRootPath)
            
        # if copy file method is chosen
        if copy:
            try:
                newf = srcFile.copyTo(os.path.join(dstDir.getPath(), srcFile.getName()+srcFile.getExt()))
                if indexing: 
                    newf.setIndex()
                return newf

            except indx.FileIndexingError as e:
                newf.delete() # rollback
                raise FileImportingError("Could not import file %s: %s" %(srcFile.getPath(), e))
            
            except FileExistsError as e:
                raise FileImportingError("Could not import file %s: %s"%(srcFile.getPath(), e))
        
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
                raise FileImportingError("Could not import file %s: %s" %(srcFile.getPath(), e))
            
            except FileExistsError as e:
                raise FileImportingError("Could not import file %s"%(srcFile.getPath(), e))                 

    except KeyError as e:
        raise e

def importFiles(srcFiles, dstRootPath, organizeBy=None, copy=True, indexing=True):
    """
    TODO: remove
    TODO: Test rollbacks
    TODO: param srcFiles must be a unique srcFile!!
    Imports media files to a destination, in filesystem
    This function does not deal with metadata
    @param srcFiles: List of File objects to be imported. Files must be of a valid media type
    @param dstRootPath: Root of destination directory 
    @param organizeBy: Files organizational method. Available options are defined in the preferences module. If None(default), all files are imported to root
    @param copy: If true, files are copied instead of being moved. Defaults to True
    @param indexing: If true, files are automatically indexed on importing. Defaults to True
    """    
    for f in srcFiles:
        try:
            # find out the target directory for file
            if organizeBy is not None: # use some organizational method
                dstDir = IMPORTING_ORGANIZE_BY[organizeBy](dstRootPath,f)            
            else: # import all files to root dir
                dstDir = dstRootPath
                
            # create Directory object (and path in filesystem if it did not exist)
            try: 
                dstDir = Directory(dstRootPath)
            except NotADirectoryError:
                os.makedirs(dstRootPath)
                dstDir = Directory(dstRootPath)
                
            # if copy file method is chosen
            if copy:
                try:
                    newf = f.copyTo(os.path.join(dstDir.getPath(), f.getName()+f.getExt()))
                    if indexing: 
                        newf.setIndex()
    
                except indx.FileIndexingError as e:
                    newf.delete() # rollback
                    raise FileImportingError("Could not import file %s: %s" %(f.getPath(), e))
                
                except FileExistsError as e:
                    raise FileImportingError("Could not import file %s: %s"%(f.getPath(), e))
            
            # if move file method is chosen                          
            else:
                try:
                    oldPath = f.getPath()
                    f.moveTo(os.path.join(dstDir.getPath(), f.getName()+f.getExt()))
                    if indexing:
                        f.setIndex()
                
                except indx.FileIndexingError as e:
                    f.moveTo(oldPath) # rollback
                    raise FileImportingError("Could not import file %s: %s" %(f.getPath(), e))
                
                except FileExistsError as e:
                    raise FileImportingError("Could not import file %s"%(f.getPath(), e))                 

        except KeyError as e:
            raise e


def importMedia():
    ''' TODO: Moves media to database 
    MOVE TO TOP MODULE
    @param copy: Defines whether media should be moved to directory before it is imported
    '''
    pass

class FileImportingError(Exception):
    pass

def main():
    '''
        Main function
    '''
    srcDir = r'G:\videos_sentinelas'
    srcfiles = [File(os.path.join(srcDir, f), "footage") for f in os.listdir(srcDir) if os.path.isfile(os.path.join(srcDir, f))]
    for f in srcfiles:
        pass
        
    srcFile = srcfiles[0]
    importFile(srcFile, r'G:\cariama\mediadb\quarantine', organizeBy='date%Y%m')
    
    


    
    

    
if __name__=='__main__':
    main()
    