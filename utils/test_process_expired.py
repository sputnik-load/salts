import unittest
import os
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
from datetime import timedelta
import ConfigParser
from optparse import OptionParser
from process_expired import ExpiredHandler
from process_expired import Logger
from process_expired import TimeConfigError
from process_expired import DBConfigError
from process_expired_const import *

logger = Logger()
TIME_CONFIG_INI = "test_process_expired.ini"
DB_SETTINGS_INI = "test_db_settings.ini"
TEST_FOLDER = "test_files"
TEST_DB_NAME = "test_db"
TEST_TABLE_NAME = "salts_testresult"
TEST_RESULTS_DIR = "test_results"
TEST_LOG = "test.log"
CSV_NAME = "data.csv"
ROOT_PATH = "."

def create_test_folder(base_name, root = ROOT_PATH):
    i = 0
    while True:
        folder_path = "%s/%s-%d" % (root, base_name, i)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            return folder_path
        i += 1

def generate_test_file(base_name, folder = TEST_FOLDER):
    i = 0
    base_file_path = "%s/%s" % (folder, base_name)
    file_path = base_file_path
    while True:
        if not os.path.exists(file_path):
            f = open(file_path, "w")
            f.write("0" * 1000)
            f.close()
            return file_path
        file_path = "%s.%d" % (base_file_path, i)
        i += 1

def create_test_database():
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
                    "localhost", "postgres", "test", "test")
    conn = psycopg2.connect(conn_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = '%s'" % TEST_DB_NAME)
    if not cur.fetchall():
        cur.execute("CREATE DATABASE %s" % TEST_DB_NAME)
    cur.close()
    conn.close()

def log_name_exists(conn, log_type, log_name):
    cur = conn.cursor()
    query = "SELECT id FROM %s WHERE %s = '%s'" % (TEST_TABLE_NAME, log_type, log_name)
    cur.execute(query)
    result = True
    if not cur.fetchall():
        resut = False
    cur.close()
    return result

class TestProcessExpired(unittest.TestCase):

    def _create_test_options(self, temp_folder_path = ""):
        parser = OptionParser()
        parser.add_option("--tr-path", default = self._tr_path)
        parser.add_option("--db-name", default = self._db_name)
        parser.add_option("--log-filename", default = self._test_log)
        parser.add_option("--dry-run", default = False)
        parser.add_option("--verbose", default = False)
        parser.add_option("--quiet", default = True)
        (self._options, args) = parser.parse_args()

    def _create_test_table(self):
        cur = self._conn.cursor()
        query = """CREATE TABLE IF NOT EXISTS %s (
                        id SERIAL,
                        dt_finish TIMESTAMP WITH TIME ZONE,
                        metrics VARCHAR(100),
                        jm_jtl VARCHAR(100),
                        phout VARCHAR(100),
                        yt_log VARCHAR(100),
                        jm_log VARCHAR(100),
                        ph_conf VARCHAR(100),
                        yt_conf VARCHAR(100),
                        modified_jmx VARCHAR(100),
                        console_log VARCHAR(100),
                        report_txt VARCHAR(100),
                        jm_log_2 VARCHAR(100)
                    )
                """ % TEST_TABLE_NAME
        cur.execute(query)
        self._conn.commit()
        cur.close()

        
    def _drop_test_table(self):
        cur = self._conn.cursor()
        cur.execute("DROP TABLE %s;" % TEST_TABLE_NAME)
        self._conn.commit()
        cur.close()

    def _data2csv(self, test_data, log_path):
        columns = ["metrics", "jm_jtl", "phout", "yt_log", "jm_log",
                    "ph_conf", "yt_conf", "modified_jmx", "console_log", 
                    "report_txt", "jm_log_2"]
        cur_dt = datetime.now()
        with open(self._csv_path, "w") as csv_file:
            i = 1
            k = 10
            for col in columns:        
                for case in test_data[col]:
                    period = case[0]
                    file_name = "%s.%s" % (col, period)
                    file_path = generate_test_file(file_name, log_path)
                    tr_file_path = re.sub("^%s/" % ROOT_PATH, "", file_path)
                    dt = cur_dt - timedelta(days = period)
                    csv_file.write("%s%s%s%s\n" % (dt.strftime("%Y-%m-%d %H:%M:%S"), 
                                                    ";" * i, tr_file_path, ";" * k))
                    case.append(tr_file_path)
                i += 1
                k -= 1

    def _load_csv(self):        
        cur = self._conn.cursor()
        query = """COPY %s (dt_finish, metrics, jm_jtl, phout, yt_log, jm_log,
                            ph_conf, yt_conf, modified_jmx, console_log,
                            report_txt, jm_log_2) 
                    FROM '%s' DELIMITER ';' CSV;
                """ % (TEST_TABLE_NAME, self._csv_path) 
        cur.execute(query)
        self._conn.commit()
        cur.close()

    def _check_archive(self, test_data): 
        for log_type in test_data:
            for case in test_data[log_type]: 
                archive = case[1]
                file_path = case[2]
                if archive:
                    arch_path = "%s.gz" % file_path
                    self.assertTrue(os.path.exists(arch_path),
                        "File %s is absent." % arch_path)
                    self.assertTrue(
                        log_name_exists(self._conn, log_type, arch_path),
                        "Record with %s isn't exist." % arch_path)
                else:
                    self.assertTrue(os.path.exists(file_path),
                        "File %s is absent." % file_path)
                    self.assertTrue(
                        log_name_exists(self._conn, log_type, file_path),
                        "Record with %s isn't exist." % file_path)

    def _check_remove(self, test_data): 
        for log_type in test_data:
            for case in test_data[log_type]: 
                remove = case[1]
                file_path = case[2]
                if remove:
                    self.assertTrue(not os.path.exists(file_path),
                        "File %s is exist (should be removed)." % file_path)
                    self.assertTrue(
                        log_name_exists(self._conn, log_type, file_path),
                        "Record with %s is exist (should be empty)." % file_path)
                else:
                    self.assertTrue(os.path.exists(file_path),
                        "File %s isn't exist." % file_path)
                    self.assertTrue(
                        log_name_exists(self._conn, log_type, file_path),
                        "Record with %s isn't exist." % file_path)
                    
    def setUp(self):
        self._tr_path = TEST_RESULTS_DIR
        self._db_name = TEST_DB_NAME
        self._test_log = TEST_LOG
        self._csv_path = "%s/%s" % (os.getcwd(), CSV_NAME)

    def tearDown(self):
        if os.path.exists(self._csv_path):
            os.remove(self._csv_path)

    def test_time_config_absent(self):
        self._create_test_options()
        tmp_name = "%s.copy" % TIME_CONFIG_INI
        os.rename(TIME_CONFIG_INI, tmp_name)
        self.assertRaises(TimeConfigError, ExpiredHandler,
                            self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        os.rename(tmp_name, TIME_CONFIG_INI)


    def test_db_settings_absent(self):
        self._create_test_options()
        tmp_name = "%s.copy" % DB_SETTINGS_INI
        os.rename(DB_SETTINGS_INI, tmp_name)
        self.assertRaises(DBConfigError, ExpiredHandler,
                            self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        os.rename(tmp_name, DB_SETTINGS_INI)

    def test_time_config_section_absent(self):
        self._create_test_options()
        config = ConfigParser.RawConfigParser()
        config.read(TIME_CONFIG_INI)
        config.remove_section("metrics")
        with open(TIME_CONFIG_INI, 'wb') as configfile:
            config.write(configfile)
        self.assertRaises(TimeConfigError, ExpiredHandler,
                            self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        config.add_section("metrics")
        with open(TIME_CONFIG_INI, 'wb') as configfile:
            config.write(configfile)

    def test_time_config_option_absent(self):
        self._create_test_options()
        config = ConfigParser.RawConfigParser()
        config.read(TIME_CONFIG_INI)
        config.remove_option("DEFAULT", "archive")
        with open(TIME_CONFIG_INI, "wb") as configfile:
            config.write(configfile)
        self.assertRaises(TimeConfigError, ExpiredHandler,
                            self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        config.set("DEFAULT", "archive", TC_NO_TOUCH)
        with open(TIME_CONFIG_INI, 'wb') as configfile:
            config.write(configfile)

    def test_db_config_section_absent(self):
        self._db_name = "fake_db_name"
        self._create_test_options()
        self.assertRaises(DBConfigError, ExpiredHandler,
                            self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)

    def test_db_config_option_absent(self):
        self._create_test_options()
        config = ConfigParser.RawConfigParser()
        config.read(DB_SETTINGS_INI)
        config.remove_option(self._options.db_name, "host")
        with open(DB_SETTINGS_INI, 'wb') as configfile:
            config.write(configfile)
        self.assertRaises(DBConfigError, ExpiredHandler,
                            self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        config.set(self._options.db_name, "host", "localhost")
        with open(DB_SETTINGS_INI, "wb") as configfile:
            config.write(configfile)

    def test_archive(self):
        self._create_test_options()
        eh = ExpiredHandler(self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        self._conn = eh.connect_db()
        self._create_test_table()
        test_folder = create_test_folder(TEST_FOLDER)
        test_data = {"metrics": [[0, False], [180, False], [181, True]],
                    "jm_jtl": [[0, False], [30, False], [31, True]],
                    "phout": [[0, False], [30, False], [31, True]],
                    "yt_log": [[0, False], [30, False], [31, True]],
                    "jm_log": [[0, False], [30, False], [31, True]],
                    "yt_conf": [[0, False], [365, False], [366, True]],
                    "ph_conf": [[0, False], [365, False], [366, True]],
                    "modified_jmx": [[0, False], [180, False], [181, True]],
                    "console_log": [[0, False], [30, False], [31, True]],
                    "report_txt": [[0, False], [366, False]],
                    "jm_log_2": [[0, False], [30, False], [31, True]]
                }
        self._data2csv(test_data, test_folder)
        self._load_csv()
        eh.archive()
        self._check_archive(test_data)
        self._drop_test_table()
        eh.disconnect_db()


    def test_remove(self): 
        self._create_test_options()
        eh = ExpiredHandler(self._options, logger,
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        self._conn = eh.connect_db()
        self._create_test_table()
        test_folder = create_test_folder(TEST_FOLDER)
        test_data = {"metrics": [[0, False], [366, False]],
                    "jm_jtl": [[0, False], [366, False]],
                    "phout": [[0, False], [366, False]],
                    "yt_log": [[0, False], [30, False], [31, True]],
                    "jm_log": [[0, False], [30, False], [31, True]],
                    "yt_conf": [[0, False], [365, False], [366, True]],
                    "ph_conf": [[0, False], [365, False], [366, True]],
                    "modified_jmx": [[0, False], [180, False], [181, True]],
                    "console_log": [[0, False], [30, False], [31, True]],
                    "report_txt": [[0, False], [366, False]],
                    "jm_log_2": [[0, False], [30, False], [31, True]]
                }
        self._data2csv(test_data, test_folder)
        self._load_csv()
        eh.remove()
        self._check_remove(test_data)
        self._drop_test_table()
        eh.disconnect_db()

if __name__ == "__main__":
    create_test_database()
    unittest.main()

