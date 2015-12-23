'''
Created on Dec 20, 2015

@author: PEDRO
'''

import unittest, os, shutil, filecmp
from fdmgm import File, Directory
import indexing as indx


class TestFileMethods(unittest.TestCase):
    
    def setUp(self):
        """ Creates two different files on fixtures directory for testing """
        os.makedirs(os.path.abspath("fixtures"))
        fpath = os.path.abspath("fixtures/tgtfile.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(2048))
            
        self.tgtfile = File(fpath)
        
        fpath = os.path.abspath("fixtures/testfile.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(1024))
            
        self.testfile = File(fpath)
                
    def test_files_are_different(self):
        """ Makes sure target and test files are different """
        self.assertFalse(filecmp.cmp(self.tgtfile.getPath(), self.testfile.getPath()), "files are equal!")
  
    def test_file_constructor_accepts_valid_path(self):
        """ A file instance can be created with a path pointing to a existing file """
        validPath = os.path.abspath("fixtures/testfile.dat")
        self.assertTrue(os.path.isfile(validPath))
        file = File(validPath)   
        self.assertTrue('file' in vars())
           
    def test_file_constructor_does_not_accept_invalid_path(self):
        """ If a file tries to be created with a non-existent file, constructor raises error """       
        invalidPath = os.path.abspath("fixtures/invalidfile.dat")
        self.assertFalse(os.path.isfile(invalidPath))
        with self.assertRaises(FileNotFoundError):
            file = File(invalidPath)          
        self.assertFalse('file' in vars())
        with self.assertRaises(FileNotFoundError):
            File(None)
 
    def test_file_exists(self):
        """ Method .exists works """
        self.assertTrue(self.testfile.exists())
        self.testfile.unlink()
        self.assertFalse(self.testfile.exists())

    def test_file_unlink(self):
        """ Method .unlink sets instance path to None """
        self.testfile.unlink()
        self.assertIsNone(self.testfile.getPath())
 
    def test_file_instance_may_end_having_reference_broken(self):
        """ Shows that a file instance may have a broken reference if file is deleted from directory """
        os.remove(self.testfile.getPath())
        self.assertFalse(self.testfile.exists())
        self.assertIsInstance(self.testfile, File)  
        
    def test_file_cannot_get_size_from_invalid_file(self):
        #TODO
        pass
    
    def test_rename_file_does_not_overwrite(self):
        """ Method .setName does not accidentally overwrite files """
        with self.assertRaises(FileExistsError):
            self.testfile.setName(self.tgtfile.getName()) # overwrite another file
        with self.assertRaises(FileExistsError):
            self.testfile.setName(self.testfile.getName()) # overwrite same file
    
    def test_rename_changes_file_attribute_name(self):
        """ Method .setName does change File object name (path) attribute"""
        newName = "anotherName"
        self.testfile.setName(newName)
        self.assertEqual(self.testfile.getName(), newName)
        
    def test_rename_file_exists_after_renaming(self):
        """ File object renamed by method .setName also exists in directory """
        newName = "anotherName"
        self.testfile.setName(newName)
        self.assertTrue(self.testfile.exists())
             
    def test_copy_file_does_not_overwrite(self): 
        """ Method .copyTo does not accidentally overwrite files """
        with self.assertRaises(FileExistsError):
            self.testfile.copyTo(self.tgtfile.getPath()) # overwrite another file
            self.testfile.copyTo(self.testfile.getPath()) # overwrite same file
        
    def test_copy_file_returns_valid_object(self):
        """ Method .copyTo returns a valid (existing) File object with the same media type and content"""    
        self.testfile.setMediaType('somemedia')
        newFile = self.testfile.copyTo("fixtures/copy/"+self.testfile.getName()+self.testfile.getExt())
        self.assertTrue(newFile.exists())
        self.assertTrue(filecmp.cmp(self.testfile.getPath(), newFile.getPath()), "Different files")
        self.assertEqual(newFile.getMediaType(), self.testfile.getMediaType(), "Different media types")
    
    def test_copy_file_preserves_original_file(self):
        """ Method .copyTo preserves original file """
        originalPath = self.testfile.getPath()
        self.testfile.copyTo("fixtures/copy/" + "newfile" + self.testfile.getExt())
        self.assertTrue(self.testfile.exists())
        self.assertTrue(os.path.isfile(originalPath))
    
    def test_copy_file_preserves_date(self):
        """ Method .copyTo preserves file modification and access date """
        originalTs = self.testfile.getDate()
        newFile = self.testfile.copyTo("fixtures/copy/newfile"+self.testfile.getExt(), preserveDate=True)
        self.assertEqual(originalTs['mtime'], newFile.getDate()['mtime'])
        self.assertEqual(originalTs['atime'], newFile.getDate()['atime'])
    
    def test_move_file_does_not_overwrite(self):
        """ Method .moveTo does not accidentally overwrite files """
        with self.assertRaises(FileExistsError):
            self.testfile.moveTo(self.tgtfile.getPath()) # overwrite another file
            self.testfile.moveTo(self.testfile.getPath()) # overwrite same file
            
    def test_move_file_returns_valid_object(self):
        """ Method .moveTo returns a valid (existing) File object with the same medi type and content """
        self.testfile.setMediaType('somemedia')
        newFile = self.testfile.moveTo("fixtures/move/newfile" + self.testfile.getExt())
        self.assertTrue(newFile.exists())
        self.assertTrue(newFile.getMediaType()=="somemedia")
        
    def test_move_file_discards_original_file(self):
        """ Method .moveTo removes the original file (moving routine) """  
        originalPath = self.testfile.getPath()
        self.testfile.moveTo("fixtures/move/newfile" + self.testfile.getExt())
        self.assertNotEqual(self.testfile.getPath(), originalPath)
        self.assertFalse(os.path.isfile(originalPath))
          
    def test_move_file_unlinks_original_file_path(self):
        """ Method .moveTo updates original File instance path to None, to avoid broken link """    
        self.testfile.moveTo("fixtures/move/newfile" + self.testfile.getExt())   
        self.assertIsNone(self.testfile.getPath())
             
    def tearDown(self):
        shutil.rmtree(os.path.abspath("fixtures"))


class TestDirectoryMethods(unittest.TestCase):
    
    def setUp(self):
        """ Creates directory and subdirectories for each test """
        os.makedirs(os.path.abspath("fixtures/testdir1/testsubdir1"))
        os.makedirs(os.path.abspath("fixtures/testdir1/testsubdir2"))
        os.makedirs(os.path.abspath("fixtures/testdir2/testsubdir1"))
        os.makedirs(os.path.abspath("fixtures/testdir2/testsubdir2"))
        
        # test directory object
        self.testdir=Directory(os.path.abspath("fixtures/testdir1"))
        self.assertTrue(self.testdir.exists())
        
        # test file object       
        fpath = "fixtures/testdir1/testfile.dat"
        with open(os.path.abspath(fpath), 'wb') as f:
            f.write(os.urandom(1024))
        self.testfile = File(fpath)

    def tearDown(self):
        """ Cleans up after each test """
        shutil.rmtree(os.path.abspath("fixtures"))

    def test_dir_constructor_accepts_valid_path(self):
        """ Directory object can be constructed if input path is valid """
        self.assertIsInstance(Directory(os.path.abspath("fixtures/testdir1")), Directory)
        
    def test_dir_constructor_does_not_accept_invalid_path(self):
        """ Directory object cannot be constructed with invalid input path """
        invalidPath = os.path.abspath("fixtures/invalidDir")
        with self.assertRaises(NotADirectoryError):
            Directory(os.path.abspath(invalidPath))
        with self.assertRaises(NotADirectoryError):
            Directory(None)
        
    def test_dir_unlink(self):
        """ Method .unlink sets directory instance path to None """
        testDir = Directory(os.path.abspath("fixtures/testdir1"))
        testDir.unlink()
        self.assertIsNone(testDir.getPath())
    
    def test_dir_exists(self):
        """ Method .exists works """
        self.assertTrue(self.testdir.exists())
        self.assertTrue(Directory(os.path.abspath("fixtures/testdir2/testsubdir1")).exists())
        shutil.rmtree(os.path.abspath("fixtures/testdir1"))
        self.assertFalse(self.testdir.exists())
        self.testdir.unlink()
        self.assertFalse(self.testdir.exists())
    
    def test_dir_instance_may_end_having_reference_broken(self):
        """ Shows that a directory instance may have a broken reference if dir is deleted from filesystem """
        shutil.rmtree(os.path.abspath("fixtures/testdir1"))
        self.assertFalse(self.testdir.exists())
        self.assertIsInstance(self.testdir, Directory)
        
    def test_dirs_get_size_gets_size_of_files(self):
        """ Method .getSize returns the size of files inside directory """
        # create a second test file
        secFPath = os.path.abspath("fixtures/testdir1/testfile2.dat")
        with open(secFPath, 'wb') as f:
            f.write(os.urandom(2048))
        secTestFile =  File(secFPath)   
        # make sure method returns the sum of the two files
        fsSizeSum = self.testfile.getSize() + secTestFile.getSize()
        self.assertEqual(self.testdir.getSize(), fsSizeSum) 
        
    def test_dirs_get_size_recursive_mode(self):
        """ Shows that:
             when getSize() is called in recursive mode size of file in subdir is included 
             when getSize() is called in non-recursive mode file in subdir is not included
             recursive and non-recursive are equivalent for 1-level dir
        """
        # create test file in subdir
        subFPath = os.path.abspath("fixtures/testdir1/testsubdir1/subfile.dat")
        with open(subFPath, 'wb') as f:
            f.write(os.urandom(1024))
        subTestFile = File(subFPath)
        # makes sure recursive mode includes file in subdir
        fsSizeSum = self.testfile.getSize() + subTestFile.getSize()
        self.assertEqual(fsSizeSum, self.testdir.getSize(recursive=True))   
        # makes sure non-recursive mode does not include file in subdir
        self.assertEqual(self.testfile.getSize(), self.testdir.getSize(recursive=False))
        # recursive and non-recursive equivalence
        shutil.rmtree("fixtures/testdir1/testsubdir1")
        self.assertEqual(self.testdir.getSize(), self.testdir.getSize())     
    
    def test_dirs_cannot_get_size_from_invalid_directory(self):
        """ Method .getSize fails for invalid directory and raises NotADirectoryError """
        shutil.rmtree(self.testdir.getPath())
        with self.assertRaises(NotADirectoryError):
            self.testdir.getSize()
        self.assertIsNone(self.testdir.unlink())
        with self.assertRaises(NotADirectoryError):
            self.testdir.getSize()
    
    def test_dirs_do_not_overwrite(self):
        #TODO
        pass
    
    def test_dirs_get_dirs_recursive_mode(self):
        """ Shows that:
             when getDirs() is called in recursive mode dir in subdirs is included 
             when getDirs() is called in non-recursive mode dir in subdir is not included
             recursive and non-recursive are equivalent for 1-level dir
        """
        infraDir = os.path.abspath("fixtures/testdir1/testsubdir1/testinfradir")
        os.makedirs(infraDir)
        # on recursive mode infradir is included
        self.assertTrue(infraDir in [d.getPath() for d in self.testdir.getDirs(recursive=True)])
        # on non-recursive mode infradir is not included
        self.assertFalse(infraDir in [d.getPath() for d in self.testdir.getDirs(recursive=False)])
        # recursive and non-recursive equivalence
        shutil.rmtree(infraDir)
        lsRec = [d.getPath() for d in self.testdir.getDirs(recursive=True)]
        lsNonRec = [d.getPath() for d in self.testdir.getDirs(recursive=False)]
        self.assertEqual(lsRec, lsNonRec)
    
    def test_dirs_get_dirs_returns_list_of_dir_objects(self):
        """ Method .getDirs returns a list of dir objects that are contained in root (test) directory """
        for item in self.testdir.getDirs():
            self.assertIsInstance(item, Directory)
    
    def test_dirs_get_dirs_does_not_contain_root(self):
        """ List returned by .getDirs does not contain the root directory, on which method was called """
        for item in self.testdir.getDirs():
            self.assertNotEqual(self.testdir.getPath(), item.getPath())
    
    def test_dirs_get_dirs_cannot_be_called_from_invalid_directory(self):
        """ Method getDirs() throws an exception if called from an invalid instance """
        shutil.rmtree(self.testdir.getPath())
        with self.assertRaises(NotADirectoryError):
            self.testdir.getDirs()   
        # sets path reference to none     
        self.assertIsNone(self.testdir.unlink())
        with self.assertRaises(NotADirectoryError):
            self.testdir.getDirs()

    def test_dirs_get_dirs_keeps_directory_media_type(self):
        """ Child directories retrieved by .getFiles method are set as same media types """
        mediaType = "somemedia"
        self.testdir.setMediaType(mediaType)
        for item in [d.getMediaType() for d in self.testdir.getDirs()]:
            self.assertEqual(item, mediaType)
        self.testdir.setMediaType(None)
        for item in [d.getMediaType() for d in self.testdir.getDirs()]:
            self.assertIsNone(item)

    def test_dirs_get_files_returns_list_of_file_objects(self):
        """ Method .getFiles returns a list of file objects that are contained in root (test) directory """
        for item in self.testdir.getFiles():
            self.assertIsInstance(item, File)
          
    def test_dirs_get_files_recursive_mode(self):
        """ Shows that:
             when getFiles() is called in recursive mode file in subdir is included 
             when getfiles() is called in non-recursive mode file in subdir is not included
             recursive and non-recursive are equivalent for 1-level dir
        """
        pass
        infraDir = os.path.abspath("fixtures/testdir1/testsubdir1/testinfradir")
        infraFilePath = os.path.abspath("fixtures/testdir1/testsubdir1/testinfradir/infratestfile.dat")
        os.makedirs(infraDir)
        with open(infraFilePath, 'wb') as f:
            f.write(os.urandom(1024))            
        # on recursive mode file in infradir is included
        self.assertTrue(infraFilePath in [file.getPath() for file in self.testdir.getFiles(recursive=True)])
        # on non-recursive mode infradir is not included
        self.assertFalse(infraFilePath in [file.getPath() for file in self.testdir.getFiles(recursive=False)])
        # recursive and non-recursive equivalence           
        shutil.rmtree(infraDir)
        lsRec = [file.getPath() for file in self.testdir.getFiles(recursive=True)]
        lsNonRec = [file.getPath() for file in self.testdir.getFiles(recursive=False)]
        self.assertEqual(lsRec, lsNonRec)
    
    def test_dirs_get_files_cannot_be_called_from_invalid_directory(self):
        """ Method getFiles() throws an exception if called from an invalid directory instance """
        shutil.rmtree(self.testdir.getPath())
        with self.assertRaises(NotADirectoryError):
            self.testdir.getFiles()   
        # sets path reference to none     
        self.assertIsNone(self.testdir.unlink())
        with self.assertRaises(NotADirectoryError):
            self.testdir.getFiles()
    
    def test_dirs_get_files_keeps_directory_media_type(self):
        """ Files retrieved by .getFiles method are set as same media types """
        mediaType = "somemedia"
        self.testdir.setMediaType(mediaType)
        for item in [f.getMediaType() for f in self.testdir.getFiles()]:
            self.assertEqual(item, mediaType)      
        self.testdir.setMediaType(None)
        for item in [f.getMediaType() for f in self.testdir.getFiles()]:
            self.assertIsNone(item)
      
        
class TestIndexing(unittest.TestCase):
    
    def setUp(self):
        """ Creates test file to be indexed """
        os.makedirs(os.path.abspath("fixtures"))
        fpath = os.path.abspath("fixtures/testfile.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(2048))
        self.testFile = File(fpath)
        
    def tearDown(self):
        shutil.rmtree(os.path.abspath("fixtures"))
        
    def test_prefixing_unknown_mediatype_raises_exception(self):
        """ getPrefix() function raises exception for unknown or None media type """     
        self.testFile.setMediaType("unknown")        
        with self.assertRaises(ValueError):
            indx.getPrefix(self.testFile)
                         
        self.testFile.setMediaType(None)
        with self.assertRaises(ValueError):
            indx.getPrefix(self.testFile)
   
    def test_number_format_to_string_strict(self):     
        """ Tests number-to-string formatting function on strict mode """      
        # Outputs n-lenghted string when number length is smaller than parameter 
        n=4
        self.assertEqual(len(indx.numberFormatToString(999, length=n, strict=True)), n)
        
        # Ouputs n-lengthed string when number length is equal parameter
        self.assertEqual(len(indx.numberFormatToString(9999, length=n, strict=True)), n)
        
        # Raises error when number is not int
        with self.assertRaises(TypeError):
            indx.numberFormatToString(3.5, strict=True)
        
        # Raises error when number length is higher than parameter
        with self.assertRaises(ValueError):
            indx.numberFormatToString(10000, length=4, strict=True)
        
        # Raises error when number is negative
        with self.assertRaises(ValueError):
            indx.numberFormatToString(-1, strict=True)
        
        # Returns None when length < 1    
        self.assertEqual(indx.numberFormatToString(333, length=0, strict=True), None)
        self.assertEqual(indx.numberFormatToString(333, length=-1, strict=True), None)
            
    def test_number_format_to_string_not_strict(self):
        """ Tests number-to-string formatting function on non-strict mode """
        # Outputs n-lenghted string when number length is smaller than parameter 
        n=4
        self.assertEqual(len(indx.numberFormatToString(999, length=n, strict=False)), n)

        # Outputs n-lenghted string when number length is greater than parameter
        self.assertEqual(len(indx.numberFormatToString(10000, length=n, strict=False)), n)
          
        # Ouputs n-lengthed string when number length is equal parameter
        self.assertEqual(len(indx.numberFormatToString(9999, length=n, strict=False)), n)
        
        # Assures trailing numbers get discarded when number length > length parameter
        self.assertFalse("9" in indx.numberFormatToString(11119, length=4, strict=False))
        
        # Raises error when number is not int
        with self.assertRaises(TypeError):
            indx.numberFormatToString(3.5, strict=False)
        
        # Raises error when number is negative
        with self.assertRaises(ValueError):
            indx.numberFormatToString(-1, strict=False)
        
        # Returns None when length < 1    
        self.assertEqual(indx.numberFormatToString(333, length=0, strict=False), None)
        self.assertEqual(indx.numberFormatToString(333, length=-1, strict=False), None)

    def test_indexing_renames_file(self):
        """ indexFile() function changes file name """
        oldName = self.testFile.getName()
        indx.indexFile(self.testFile, prefix="PREF")
        newName = self.testFile.getName()
        self.assertNotEqual(oldName, newName)
        
    def test_indexing_auto_prefix_on_unknown_media_file_raises_exception(self):
        """ indexFile() with auto prefix raises exception for unknown or None media types """
        self.testFile.setMediaType(None)
        with self.assertRaises(ValueError):
            indx.indexFile(self.testFile)  
        self.testFile.setMediaType("unknown")
        with self.assertRaises(ValueError):
            indx.indexFile(self.testFile)
           
            
def main():
    
    open(os.path.abspath("file.txt"),'a').close()
    
if __name__=="__main__":
    unittest.main()