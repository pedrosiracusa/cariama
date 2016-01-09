'''
Created on Dec 20, 2015

@author: PEDRO
'''

import unittest, os, shutil, filecmp
from fdmgm import File, Directory
import fdmgm as mgm
import indexing as indx
import preferences as prefs


class TestFileMethods(unittest.TestCase):
    
    def setUp(self):
        """ Creates three different files on fixtures directory for testing """
        os.makedirs(os.path.abspath("fixtures/subdir"))
        fpath = os.path.abspath("fixtures/tgtfile.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(2048))            
        self.tgtfile = File(fpath)
        
        fpath = os.path.abspath("fixtures/subdir/tgtfile2.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(4096))
        self.tgtsubfile = File(fpath)
        
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
        with self.assertRaises(FileExistsError):
            self.testfile.copyTo(self.testfile.getPath()) # overwrite same file
        with self.assertRaises(FileExistsError):
            self.testfile.copyTo(self.tgtsubfile.getPath()) # overwrite file in another dir
        
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
        with self.assertRaises(FileExistsError):
            self.testfile.moveTo(self.testfile.getPath()) # overwrite same file
        with self.assertRaises(FileExistsError):
            self.testfile.copyTo(self.tgtsubfile.getPath()) # overwrite file in another dir            
            
    def test_move_file_does_not_return_valid_object(self):
        """ Method .moveTo does not return a valid File object, as opposed to copyTo()"""
        self.testfile.setMediaType('somemedia')
        returnVal = self.testfile.moveTo("fixtures/move/newfile" + self.testfile.getExt())
        self.assertIsNone(returnVal)
        
    def test_move_file_discards_original_file(self):
        """ Method .moveTo removes the original file (moving routine) """  
        originalPath = self.testfile.getPath()
        self.testfile.moveTo("fixtures/move/newfile" + self.testfile.getExt())
        self.assertNotEqual(self.testfile.getPath(), originalPath)
        self.assertFalse(os.path.isfile(originalPath))
 
    def test_set_index_does_not_accept_invalid_media_type(self):
        """ setIndex method does not index file with invalid media type """
        self.testfile.setMediaType(None)
        with self.assertRaises(indx.FileIndexingError):
            self.testfile.setIndex()      
        self.testfile.setMediaType("Unknown")
        with self.assertRaises(indx.FileIndexingError):
            self.testfile.setIndex()
           
    def test_set_index_renames_unindexed_file(self):  
        """ setIndex method successfully indexes non-indexed files """
        validType = next(iter(prefs.INDEX_PREFIX.keys()))
        self.testfile.setMediaType(validType)
        self.testfile.setIndex()
        self.assertTrue(indx.parseIndex(self.testfile.getName()))
    
    def test_set_index_does_not_rename_indexed_file(self): 
        """ setIndex method does not re-index previously indexed files """
        # first indexing
        validType = next(iter(prefs.INDEX_PREFIX.keys()))
        self.testfile.setMediaType(validType)
        self.testfile.setIndex()
        # re-indexing raises error
        with self.assertRaises(indx.FileIndexingError):
            self.testfile.setIndex()      
             
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
        
        self.validIndex = "MVDC2010080213445412345"      # just a valid index
        self.invalidIndex = {                       # a set of invalid indexes
            'wrongPref': "MCCV2010090213445412345",
            'noPref': "2010080213445412345",
            'shortDate': "MVDC201009021344512345",
            'longDate': "MVDC20100902134454412345",
            'noDate': "MVDC12345",
            'invalidDate': "MVDC2010130213445412345",
            'shortSuff': "MVDC201008021344541234",
            'longSuff': "MVDC20100802134454123456",
            'noSuff': "MVDC20100802134454",
            'noNums': "MVDC",
            'lettersInNumeric': "MVDC20100802134454MV12345"
            } 
        
    def tearDown(self):
        shutil.rmtree(os.path.abspath("fixtures"))
        
    def test_prefixing_unknown_mediatype_raises_exception(self):
        """ getPrefix() function raises exception for unknown or None media type """     
        self.testFile.setMediaType("unknown")        
        with self.assertRaises(ValueError):
            indx.getPrefix(self.testFile.getMediaType())
                         
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
        
        # Assures leading numbers get discarded when number length > length parameter
        self.assertFalse("9" in indx.numberFormatToString(91111, length=4, strict=False))
        
        # Raises error when number is not int
        with self.assertRaises(TypeError):
            indx.numberFormatToString(3.5, strict=False)
        
        # Raises error when number is negative
        with self.assertRaises(ValueError):
            indx.numberFormatToString(-1, strict=False)
        
        # Returns None when length < 1    
        self.assertEqual(indx.numberFormatToString(333, length=0, strict=False), None)
        self.assertEqual(indx.numberFormatToString(333, length=-1, strict=False), None)
        
    def test_indexing_auto_prefix_on_unknown_media_file_raises_exception(self):
        """ indexFile() with auto prefix raises exception for unknown or None media types """
        pass
           
    def test_index_parser(self):
        """ Test index parser with some dummy valid and invalid indexes """
        self.assertTrue(self.validIndex)
        for key, val in self.invalidIndex.items():
            self.assertFalse(indx.parseIndex(val))
            
    def test_index_generator_raises_exception_if_invalid(self):
        """ Function genIndex() raises value exception if generated index is invalid """
        # test for invalid prefix
        invalidPrefix = "MVTC"
        validPrefix = "MVDC"
        with self.assertRaises(ValueError):
            indx.genIndex(invalidPrefix, self.testFile.getDate()['mtime'], self.testFile.getSize())
        # test for invalid timestamp 
        with self.assertRaises(ValueError):
            indx.genIndex(validPrefix, -2, self.testFile.getSize())
        # test for invalid suffix
        with self.assertRaises(ValueError):
            indx.genIndex(validPrefix, self.testFile.getDate()['mtime'], -2)
          

class TestImporting(unittest.TestCase):
    
    def setUp(self):
        """ Creates test dir and files """
        self.validMediaType = next(iter(prefs.INDEX_PREFIX.keys()))
        os.makedirs(os.path.abspath("fixtures"))
        # test quarantine
        self.testQuarantine = os.path.abspath("fixtures/quarantine")
        os.makedirs(self.testQuarantine)
        # file1
        fpath = os.path.abspath("fixtures/mediafile1.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(2048))
        self.testfile1 = File(fpath)
        # file2
        fpath = os.path.abspath("fixtures/mediafile2.dat")
        with open(fpath, 'wb') as f:
            f.write(os.urandom(1024))
        self.testfile2 = File(fpath)
    
    def tearDown(self):
        """ Removes fixtures test dirs and files """
        shutil.rmtree(os.path.abspath("fixtures"))
    
    def test_import_file_indexing_file_copied_on_import_does_not_rename_original(self):
        """ Importing method by copying prevents original file renaming during its routine """
        origName = self.testfile1.getName()
        self.testfile1.setMediaType(self.validMediaType)
        mgm.importFile(self.testfile1, 
                        dstRootPath=self.testQuarantine,
                        copy=True,
                        indexing=True)
        self.assertEqual(origName, self.testfile1.getName())
          
    def test_import_files_rollsback_if_importing_fails(self):
        """ If there is an issue with importing a file by copy or moving, the operation rolls back """
        self.testfile1.setMediaType(self.validMediaType)
        # Error importing at indexing routine: different file already exists with the same index
        fileIndx = indx.genIndex(indx.getPrefix(self.testfile1.getMediaType()), self.testfile1.getDate()['mtime'], self.testfile1.getSize())
        diffFile = mgm.importFile(self.testfile2, self.testQuarantine, copy=True, indexing=False)
        diffFile.setName(fileIndx)
        
        # Failure by copying
        with self.assertRaises(mgm.FileImportingError):
            mgm.importFile(self.testfile1, self.testQuarantine, copy=True, indexing=True)
        # make sure only diffFile exists in import directory, and rollback occured
        self.assertEqual((len(os.listdir(self.testQuarantine))),1)
        
        # Failure by moving
        with self.assertRaises(mgm.FileImportingError):
            mgm.importFile(self.testfile1, self.testQuarantine, copy=False, indexing=True)
        # make sure original file was not discarded
        self.assertTrue(self.testfile1)
    
        
    def test_import_files_rollsback_on_keyboard_interrypt_or_system_failure(self):
        """ 
        TODO
        """
        pass

def main():
    
    open(os.path.abspath("file.txt"),'a').close()
    
if __name__=="__main__":
    unittest.main()