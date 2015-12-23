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

import os, shutil
import filecmp

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

        
        
    ''' Get Methods '''
    
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
    
    
    
    
    ''' Set Methods '''
   
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
         
    def copyTo(self, destPath, bufferSize=10485760, preserveDate=True):
        ''' 
        Copies file from current path to destination. Checks if file already exists on destination before 
        Optimized for copying large files
        @param destPath: Destination path
        @param bufferSize: Buffer size to use during copying. Default = 10MB
        @param preserveDate: Preserves the original file date. Default = True 
        @return: instance of new file object
        '''
        # Make sure target directory exists; create it if necessary
        destDir, destFName = os.path.split(destPath) 
        if not os.path.isdir(destDir):
            os.makedirs(destDir)
        
        # Check if destination file already exists in directory; Abort copying if positive
        fList = [f for f in os.listdir(destDir) if os.path.isfile(os.path.join(destDir, f))]
        for f in fList:
            if filecmp.cmp(self.__filePath, os.path.join(destDir, f)):
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
        
    
    def moveTo(self, destPath):
        ''' 
        Moves file from current path to destination. Checks if file already exists on destination before
        @param destPath: Destination path
        @return: instance of new file object
        '''
        # Make sure target directory exists; create it if necessary
        destDir, destFName = os.path.split(destPath) 
        if not os.path.isdir(destDir):
            os.makedirs(destDir)
        
        # Check if destination file already exists in directory; Abort copying if positive
        fList = [f for f in os.listdir(destDir) if os.path.isfile(os.path.join(destDir, f))]
        for f in fList:
            if filecmp.cmp(self.__filePath, os.path.join(destDir, f)):
                raise FileExistsError("[mediautils.copyTo] File %r already exists on destination" %(destFName))
  
        # Moving routine
        shutil.move(self.__filePath, destPath)
        
        self.__filePath=None
        
        return File(destPath, mediaType=self.__mediaType)
          
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
 

def toQuarantine():
    ''' TODO: 
    MOVE TO TOP MODULE
    Moves untrimmed video to quarantine, before they're included in database '''
    pass

def importMedia():
    ''' TODO: Moves media to database 
    MOVE TO TOP MODULE
    @param copy: Defines whether media should be moved to directory before it is imported
    '''
    pass

def main():
    '''
        Main function
    '''
    
    myDir = Directory(r'C:\Users\PEDRO\Desktop\videos_sentinelas', 'video')
    print(myDir.getSize())
    print(myDir.getSize(recursive=False))
    

    
    

    
if __name__=='__main__':
    main()
    