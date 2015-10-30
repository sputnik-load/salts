import unittest
import os
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

class TestProcessExpired(unittest.TestCase):

    def _create_test_options(self, temp_folder_path = ""): 
        parser = OptionParser()
        parser.add_option("--tr-path", default = "test_results")
        parser.add_option("--db-name", default = self._db_name)
        parser.add_option("--log-filename", default = "test.log")
        parser.add_option("--dry-run", default = False)
        parser.add_option("--verbose", default = False)
        parser.add_option("--quiet", default = True)
        (self._options, args) = parser.parse_args() 

    def setUp(self):
        self._db_name = "test_salts_db"

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
        with open(TIME_CONFIG_INI, 'wb') as configfile:
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

    def test_archive(self):
        self._create_test_options()
        eh = ExpiredHandler(self._options, logger, 
                            TIME_CONFIG_INI, DB_SETTINGS_INI)
        eh.archive()

if __name__ == "__main__":
    unittest.main()
