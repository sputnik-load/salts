#!/usr/bin/python

import unittest
from optparse import OptionParser
from clean_useless import UselessTR
from clean_useless import Logger
import os
import shutil
import random

test_root_path = "test_data/useless"
logger = Logger()

class TestUselessTR(unittest.TestCase):

    def _create_test_folder(self, root_path, folder_name):
        i = 0
        full_path = ""
        while 1:
            full_path = "%s/%s-%d" % (root_path, folder_name, i)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                break
            i += 1
        return full_path

    def _create_test_file(self, root_path, file_name):
        full_path = "%s/%s" % (root_path, file_name)
        fd = open(full_path, "w")
        fd.close()
        return full_path
        

    def _remove_test_folder(self, test_folder):
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)

    def _create_test_options(self): 
        self._test_result_folder_path = self._create_test_folder(test_root_path, "test-result") 
        self._subfolder_path = self._create_test_folder(self._test_result_folder_path, "results")
        self._subfolder = self._subfolder_path.split("/")[-1]
        parser = OptionParser()
        parser.add_option("--tr-path", default = self._test_result_folder_path)
        parser.add_option("--tr-subfolder", default = self._subfolder)
        parser.add_option("--log-filename", default = "test.log")
        parser.add_option("--dry-run", default = False)
        parser.add_option("--verbose", default = False)
        parser.add_option("--quiet", default = True)
        (self._options, args) = parser.parse_args() 
        return self._options

    def _add_path_prefix(self, path_prefix, file_names):
        return ["%s/%s" % (path_prefix, rec) for rec in file_names if rec]

    def _set_db_ref(self):
        if not self._db_ref:
            self._db_ref = self._tr._get_db_ref(self._db_records)
            self.assertEqual(self._db_ref, self._db_expected, 
                "Useless files isn't expected. Result: %s. Expected: %s." % (self._db_ref, self._db_expected))
            

    def setUp(self):
        self._options = self._create_test_options()

        self._test_result_empty_folder_path = self._create_test_folder(test_root_path, "empty-test-result") 
        self._empty_test_folder_path = self._create_test_folder(self._test_result_empty_folder_path, "empty-test-folder")
        self._non_empty_test_folder_path = self._create_test_folder(self._test_result_empty_folder_path, "non-empty-test-folder")
        self._create_test_file(self._non_empty_test_folder_path, "test")

        self._db_records = [
            ("1.txt", "3.abc", "dl1"), 
            ("", "dl2", "5.txt"),
            ("dl3", "", "")]
        self._db_records = [tuple(self._add_path_prefix(self._subfolder, rec)) for rec in self._db_records]
        self._db_expected = ["1.txt", "3.abc", "dl1", "dl2", "5.txt", "dl3"]
        self._db_expected = self._add_path_prefix(self._subfolder, self._db_expected)
        self._expected_ul_files = ["ul1.txt", "ul2.abc", "ul3.def"]
        existed_log_filenames = ["1.txt", "3.abc", "5.txt"] + self._expected_ul_files
        random.shuffle(existed_log_filenames)
        for elf in existed_log_filenames:
            self._create_test_file(self._subfolder_path, elf)
        self._existed_log_files = self._add_path_prefix(self._subfolder, existed_log_filenames) 
        self._expected_ul_files = self._add_path_prefix(self._subfolder_path, self._expected_ul_files)
        self._expected_dead_ref = ["dl1", "dl2", "dl3"]
        self._expected_dead_ref = self._add_path_prefix(self._subfolder, self._expected_dead_ref)
        self._tr = UselessTR(self._options, logger)
        self._db_ref = None
 
    def test_remove_empty_folders(self):
        self._tr.remove_empty_folders(self._test_result_empty_folder_path)
        self.assertEqual(os.path.exists(self._empty_test_folder_path), False, 
            "Empty %s folder exists (expected: it shouldn't be existed)." % self._empty_test_folder_path)
        self.assertEqual(os.path.exists(self._non_empty_test_folder_path), True, 
            "Non empty %s folder doesn't exist (expected: it should be existed)." % self._non_empty_test_folder_path)           
    def test_useless_files(self):
        self._set_db_ref()
        ul_files = self._tr.useless_files(self._existed_log_files, self._db_ref)
        self.assertEqual(ul_files.sort(), self._expected_ul_files.sort(), 
            "Useless files list isn't expected. Result: %s. Expected: %s" % (ul_files, self._expected_ul_files))
        self._tr.remove_useless_files(ul_files)
        for ulf in ul_files:
            self.assertEqual(os.path.exists(ulf), False, 
                "%s useless file exists (expected: it shouldn't be existed)." % ulf)

    def test_dead_db_file_references(self):
        self._set_db_ref()
        dead_ref = self._tr.dead_db_file_references(self._existed_log_files, self._db_ref)
        self.assertEqual(dead_ref.sort(), self._expected_dead_ref.sort(),
            "Dead references list isn't expected. Result: %s. Expected: %s." % (dead_ref, self._expected_dead_ref))
        self._tr.log_dead_references(dead_ref)

    def tearDown(self):
        self._remove_test_folder(self._test_result_folder_path)
        self._remove_test_folder(self._test_result_empty_folder_path)

if __name__ == "__main__":
    unittest.main()

