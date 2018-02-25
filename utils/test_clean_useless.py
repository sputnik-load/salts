#!/usr/bin/python

import unittest
from optparse import OptionParser
from clean_useless import UselessTR
from clean_useless import Logger
import os
import shutil
import random
import psycopg2

logger = Logger()

class TestUselessTR(unittest.TestCase):

    def _record_exists(self, id):
        cursor = self._tr._conn.cursor()
        query = "select * from salts_testresult where id = %s" % id
        cursor.execute(query)
        return bool(cursor.fetchall())

    def _insert_dead_references(self, ref_values):
        ref_values["session_id"] = "2015-10-16_17-18-12.8KdyK8"
        ref_values["group"] = "<PRJ_GROUP>"
        ref_values["test_name"] = "Test.Name"
        ref_values["target"] = "<TARGET_HOST>:8080"
        ref_values["version"] = "<TARGET_SYS_VERSION>"
        ref_values["rps"] = "r:line(1, 10, 1m) const(10, 60m)"
        ref_values["graph_url"] = "http://<GRAFANA_URL>/#/dashboard/db/tankresultstpl?var-system=<SYSTEM>&from=20151016T131705&to=20151016T141812"
        ref_values["generator"] = "<TANK_STATION>"
        ref_values["user"] = "<USERNAME>"
        ref_values["ticket_id"] = "TESTING-0"
        ref_values["mnt_url"] = "#LTM_URL#"
        ref_values["comment"] = "No comments."
        ref_values["test_status"] = "unk"
        query = """ insert into salts_testresult
                    (session_id, dt_start, dt_finish, \"group\",
                    test_name, target, version, rps, q99, q90, q50,
                    http_errors_perc, net_errors_perc, graph_url, generator,
                    \"user\", ticket_id, mnt_url, comments, test_status, meta,
                    metrics, jm_log, modified_jmx, ph_conf, yt_conf, yt_log,
                    console_log, report_txt, jm_jtl, phout, jm_log_2)
                    values ('%s', now(), now() + interval '1 hour', '%s',
                            '%s', '%s', '%s', '%s', 1677, 1117, 562,
                            0, 0, '%s', '%s', '%s', '%s',
                            '%s', '%s', '%s', NULL,
                            '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
                    returning id
                    """ % ( ref_values["session_id"], ref_values["group"], ref_values["test_name"],
                            ref_values["target"], ref_values["version"], ref_values["rps"],
                            ref_values["graph_url"], ref_values["generator"],
                            ref_values["user"], ref_values["ticket_id"], ref_values["mnt_url"],
                            ref_values["comment"], ref_values["test_status"],
                            ref_values["metrics"], ref_values["jm_log"],
                            ref_values["modified_jmx"], ref_values["ph_conf"],
                            ref_values["yt_conf"], ref_values["yt_log"],
                            ref_values["console_log"], ref_values["report_txt"],
                            ref_values["jm_jtl"], ref_values["phout"], ref_values["jm_log_2"])
        cursor = self._tr._conn.cursor()
        cursor.execute(query)
        self._tr._conn.commit()
        ins_id = cursor.fetchone()[0]
        return ins_id

    def _delete_dead_references(self, del_ix):
        query = "delete from salts_testresult where id = %d" % del_ix
        self._tr._conn.cursor().execute(query)
        self._tr._conn.commit()

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

    def _set_root_path(self, root_path):
        self._test_root_path = root_path

    def _create_test_options(self, temp_folder_path = ""):
        if temp_folder_path:
            if not os.path.exists(temp_folder_path):
                os.makedirs(temp_folder_path)
            self._test_result_folder_path = self._create_test_folder(
                self._test_root_path, temp_folder_path)
            self._subfolder_path = self._create_test_folder(
                self._test_result_folder_path, "results")
            self._subfolder = self._subfolder_path.split("/")[-1]
        else:
            self._test_result_folder_path = self._test_root_path
            self._subfolder = "results"
            self._subfolder_path = "%s/%s" % (self._test_result_folder_path, self._subfolder)
        parser = OptionParser()
        parser.add_option("--db-config", default = "test_db_salts.cfg")
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
        self._temp_result_folder_path = "test_data"

    def test_remove_empty_folders(self):
        self._set_root_path(self._temp_result_folder_path)
        self._options = self._create_test_options(self._temp_result_folder_path)
        self._tr = UselessTR(self._options, logger)

        test_result_empty_folder_path = self._create_test_folder(
            self._test_root_path, "empty-test-result")
        empty_test_folder_path = self._create_test_folder(
            test_result_empty_folder_path, "empty-test-folder")
        non_empty_test_folder_path = self._create_test_folder(
            test_result_empty_folder_path, "non-empty-test-folder")
        self._create_test_file(non_empty_test_folder_path, "test")

        self._tr.remove_empty_folders(test_result_empty_folder_path)
        self.assertEqual(os.path.exists(empty_test_folder_path), False,
            "Empty %s folder exists (expected: it shouldn't be existed)." %
                empty_test_folder_path)
        self.assertEqual(os.path.exists(non_empty_test_folder_path), True,
            "Non empty %s folder doesn't exist (expected: it should be existed)." %
                non_empty_test_folder_path)

        self._remove_test_folder(test_result_empty_folder_path)
        self._remove_test_folder(self._temp_result_folder_path)

    def test_useless_files(self):
        self._set_root_path(self._temp_result_folder_path)
        self._options = self._create_test_options(self._temp_result_folder_path)
        self._tr = UselessTR(self._options, logger)

        db_records = [
            (1, "1.txt", "3.abc", "dl1"),
            (2, "", "dl2", "5.txt"),
            (3, "dl3", "", "")]
        db_records = [tuple([rec[0]] + self._add_path_prefix(self._subfolder, list(rec)[1:]))                           for rec in db_records]
        db_expected = [(1, "1.txt"), (1, "3.abc"), (1, "dl1"),
                        (2, "dl2"), (2, "5.txt"), (3, "dl3")]
        db_expected = [(item[0], "%s/%s" % (self._subfolder, item[1])) for item in db_expected if item[1]]
        expected_ul_files = ["ul1.txt", "ul2.abc", "ul3.def"]
        existed_log_filenames = ["1.txt", "3.abc", "5.txt"] + expected_ul_files
        random.shuffle(existed_log_filenames)
        for elf in existed_log_filenames:
            self._create_test_file(self._subfolder_path, elf)
        existed_log_files = self._add_path_prefix(self._subfolder, existed_log_filenames)
        expected_ul_files = self._add_path_prefix(self._subfolder_path, expected_ul_files)

        db_ref = self._tr._get_db_ref(db_records)
        self.assertEqual(db_ref, db_expected,
            "Useless files isn't expected. Result: %s. Expected: %s." % (db_ref, db_expected))

        ul_files = self._tr.useless_files(existed_log_files, db_ref)
        self.assertEqual(ul_files.sort(), expected_ul_files.sort(),
            "Useless files list isn't expected. Result: %s. Expected: %s" % (
                ul_files, expected_ul_files))

        self._tr.remove_useless_files(ul_files)
        for ulf in ul_files:
            self.assertEqual(os.path.exists(ulf), False,
                "%s useless file exists (expected: it shouldn't be existed)." % ulf)
        self._remove_test_folder(self._temp_result_folder_path)

    def test_clear_db_file_references(self):
        self._set_root_path("test_results")
        self._options = self._create_test_options()
        self._tr = UselessTR(self._options, logger)

        ref_values = {}
        for lff in self._tr._log_files_fields:
            ref_values[lff] = "dl_%s" % lff
        self._expected_dead_ref = self._add_path_prefix(self._subfolder, ref_values)
        cur_ix = self._insert_dead_references(ref_values)
        db_ref = self._tr.db_file_references()
        existed_log_files = self._tr.saved_log_files()
        dead_ref = self._tr.dead_db_file_references(existed_log_files, db_ref)
        self.assertEqual(dead_ref.sort(), self._expected_dead_ref.sort(),
            "Dead references list isn't expected. Result: %s. Expected: %s." % (dead_ref, self._expected_dead_ref))
        self._tr.log_dead_references(dead_ref)
        self._tr.clear_dead_references(dead_ref)
        self._delete_dead_references(cur_ix)
        self.assertEqual(self._record_exists(cur_ix), False, "New record wasn't removed.")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()

