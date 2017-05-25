# -*- coding: utf-8 -*-

import os
import re
from settings import LT_PATH
from django.db import connection
from django.contrib.auth.models import Group
from salts.models import Scenario
from ConfigParser import ConfigParser, NoSectionError, NoOptionError, Error
from salts_prj.settings import log


def ini_files(dir_path):
    ini = []
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == '.ini':
                config = ConfigParser()
                try:
                    config.read(full_path)
                except Error, exc:
                    log.warning("Config %s is not valid: %s" %
                                (full_path, exc))
                else:
                    try:
                        test_name = config.get('sputnikreport', 'test_name')
                    except (NoSectionError, NoOptionError):
                        log.info("Config %s is not scenario: "
                                 "there is not 'test_name' option "
                                 "in the 'sputnikreport' section." %
                                 full_path)
                    else:
                        if test_name:
                            ini.append(re.sub("%s/" % dir_path, '', full_path))
                        else:
                            log.warning("Scenario %s contains "
                                        "empty 'test_name' option." %
                                        full_path)
    return ini


class IniDuplicateError(Exception):
    pass


class IniCtrlWarning(Exception):

    messages = {
        "no_load_gen": "The load generator not declared "
                       "in the {scenario_path} config.",
        "section_need": "The {scenario_path} config doesn't "
                        "contain '{section}' section.",
        "load_gen_not_suported": "The '{load_gen}' not supported.",
        "incorrect_rps_schedule": "Incorrect {load_gen} rps_schedule in the "
                                  "{scenario_path} config.",
        "undefined_target": "The '{load_gen}' load generator does not know "
                            "about target. Check the {scenario_path} config.",
        "no_test_name": "The test name is not declared in the "
                        "'test_name' option of the 'sputnikreport' section. "
                        "Check the {scenario_path} config.",
        "inaccessible_target": "The {host}:{port} target is inaccessible from "
                               "all tank hosts. Check the {scenario_path} "
                               "config.",
        "no_free_tank": "No free tank to run the test for "
                        "the {scenario_path} config.",
        "no_config_file": "The {scenario_path} config file does not exist."}

    def __init__(self, name, params):
        self.args = (name, params)
        self.name = name
        self.params = params
        log.warning(IniCtrlWarning.messages[name].format(**params))


class IniCtrl(object):

    SALTS_SECTION = 'salts'
    REPORT_SECTION = 'sputnikreport'
    DEFAULT_GROUP = 'Salts'
    SCENARIO_ID_OPTION = 'scenario_id'

    def __init__(self, root):
        self.dir_path = root
        try:
            g = Group.objects.get(name=IniCtrl.DEFAULT_GROUP)
        except Group.DoesNotExist:
            g = Group(name=IniCtrl.DEFAULT_GROUP)
            g.save()
            log.info("Group '%s' has been added." % IniCtrl.DEFAULT_GROUP)
        self.default_group_id = g.id

    def _scenario_id_from_ini(self, scenario_path):
        config = ConfigParser()
        config.read(os.path.join(self.dir_path, scenario_path))
        if not config.has_section(IniCtrl.SALTS_SECTION):
            return 0
        if config.has_option(IniCtrl.SALTS_SECTION,
                             IniCtrl.SCENARIO_ID_OPTION):
            return int(config.get(IniCtrl.SALTS_SECTION,
                                  IniCtrl.SCENARIO_ID_OPTION))
        if config.has_option(IniCtrl.SALTS_SECTION, 'test_ini_id'):
            log.info("Scenario %s: "
                     "'test_ini_id' option is deprecated. "
                     "It won't be supported in future versions. "
                     "Please use 'scenario_id' option "
                     "instead of it." % os.path.join(self.dir_path,
                                                     scenario_path))
            return int(config.get(IniCtrl.SALTS_SECTION, 'test_ini_id'))
        return 0

    def _add_scenario_id(self, scenario_path, scenario_id):
        old_scenario_id = self._scenario_id_from_ini(scenario_path)
        if scenario_id == old_scenario_id:
            return

        section_line = "[%s]" % IniCtrl.SALTS_SECTION
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        config.read(ini_path)
        if IniCtrl.SALTS_SECTION not in config.sections():
            with open(ini_path, "a") as f:
                f.write("\n%s\n" % section_line)
        content = []
        with open(ini_path, "r") as f:
            content = f.readlines()
        ix = 0
        section_found = False
        for line in content:
            strip_line = line.strip()
            if section_found:
                if re.match("^ *\[.*\]", line):
                    section_found = False
                    continue
                pat = "^ *%s *=" % IniCtrl.SCENARIO_ID_OPTION
                if re.match(pat, strip_line):
                    del(content[ix])
                    content.insert(ix, "{option} = {value}\n".format(
                                            option=IniCtrl.SCENARIO_ID_OPTION,
                                            value=scenario_id))
                    break
            if strip_line == section_line:
                section_found = True
                if not old_scenario_id:
                    content.insert(ix + 1, "{option} = {value}\n".format(
                                            option=IniCtrl.SCENARIO_ID_OPTION,
                                            value=scenario_id))
                    break
            ix += 1
        with open(ini_path, "w") as f:
            f.writelines("".join(content))

    def _last_scenario_id(self):
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM salts_scenario "
                       "ORDER BY id DESC LIMIT 1")
        res = cursor.fetchall()
        if not res:
            return 0
        return res[0][0]

    def set_scenario_status(self, scenario_path, status_value):
        try:
            t = Scenario.objects.get(scenario_path=scenario_path)
            t.status = status_value
            t.save()
            if status_value == 'D':
                del_path = os.path.join(self.dir_path, scenario_path)
                if os.path.exists(del_path):
                    os.remove(del_path)
            return True
        except Scenario.DoesNotExist:
            return False

    def get_root(self):
        return self.dir_path

    def get_scenario_pathes(self, status_value):
        res = Scenario.objects.filter(status=status_value)
        return [r.scenario_path for r in res]

    def get_scenario_id(self, scenario_path, from_db=False):
        if from_db:
            try:
                t = Scenario.objects.get(scenario_path=scenario_path)
                return t.id
            except Scenario.DoesNotExist:
                return 0
        else:
            if not self.dir_path:
                return 0
            return self._scenario_id_from_ini(scenario_path)

    def get_group_id(self, scenario_path):
        try:
            t = Scenario.objects.get(scenario_path=scenario_path)
            return t.group_id
        except Scenario.DoesNotExist:
            return 0

    def scenario_type(self, scenario_path):
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        if not os.path.exists(ini_path):
            params = {"scenario_path": scenario_path}
            raise IniCtrlWarning("no_config_file", params)

        config.read(ini_path)
        if "tank" not in config.sections():
            params = {"scenario_path": scenario_path, "section": "tank"}
            raise IniCtrlWarning("section_need", params)

        opts = config.options("tank")
        if "plugin_phantom" in opts and config.get("tank", "plugin_phantom"):
            return "phantom"
        if "plugin_jmeter" in opts and config.get("tank", "plugin_jmeter"):
            return "jmeter"
        params = {"scenario_path": scenario_path}
        raise IniCtrlWarning("no_load_gen", params)

    def get_scenario_name(self, scenario_path):
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        test_name = ''
        if os.path.exists(ini_path):
            config.read(ini_path)
            try:
                test_name = config.get(IniCtrl.REPORT_SECTION, 'test_name')
            except (NoSectionError, NoOptionError):
                log.warning("Config %s is not scenario: "
                            "there is not 'test_name' option "
                            "in the 'sputnikreport' section." % ini_path)
        else:
            log.warning("Config %s is not found." % ini_path)
        return test_name

    def get_option_value(self, scenario_path, section, option,
                         default_value=None):
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        if not os.path.exists(ini_path):
            log.warning("Config %s is not found." % ini_path)
            return None

        config.read(ini_path)
        try:
            return config.get(section, option)
        except (NoSectionError, NoOptionError):
            if default_value is None:
                log.warning("Config {path}: "
                            "there is not '{option}' option "
                            "in the '{section}' section.".format(
                                path=ini_path,
                                option=option,
                                section=section))
            return default_value

    def get_rps_sections(self, scenario_path):
        avail_types = ["phantom", "jmeter"]
        scen_type = self.scenario_type(scenario_path)
        if scen_type not in avail_types:
            params = {"load_gen": scen_type}
            raise IniCtrlWarning("load_gen_not_suported", params)
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        config.read(ini_path)
        pat = re.compile("%s.*" % scen_type)
        result = []
        for s in config.sections():
            m = pat.match(s)
            if m:
                result.append(m.group())
        if scen_type not in result:
            params = {"section": "scen_type", "scenario_path": scenario_path}
            raise IniCtrlWarning("section_need", params)
        return result

    def sync(self):
        scenario_pathes = ini_files(self.dir_path)
        absent_ini_pathes = []
        for spath in scenario_pathes:
            ini_scenario_id = self.get_scenario_id(spath, from_db=False)
            db_scenario_id = self.get_scenario_id(spath, from_db=True)
            if ini_scenario_id:
                if db_scenario_id:
                    if ini_scenario_id == db_scenario_id:
                        continue
                    else:
                        self._add_scenario_id(spath, db_scenario_id)
                else:
                    res = Scenario.objects.filter(id=ini_scenario_id)
                    group_id = self.default_group_id
                    if res:
                        if os.path.exists(os.path.join(self.dir_path,
                                                       res[0].scenario_path)):
                            msg = "Two ini files {path1} and {path2} " \
                                  "have same test id.".format(
                                      path1=spath,
                                      path2=res[0].scenario_path)
                            raise IniDuplicateError(msg)
                        else:
                            group_id = res[0].group_id
                            res[0].delete()
                    t = Scenario(id=ini_scenario_id,
                                 scenario_path=spath,
                                 group_id=group_id,
                                 status="A")
                    t.save()
            else:
                if db_scenario_id:
                    self._add_scenario_id(spath, db_scenario_id)
                else:
                    absent_ini_pathes.append(spath)
        if absent_ini_pathes:
            with open("/tmp/1.csv", "w") as f:
                id = self._last_scenario_id() + 1
                for spath in absent_ini_pathes:
                    rec = []
                    rec.append(str(id))
                    rec.append(spath)
                    rec.append("A")
                    rec.append(str(self.default_group_id))
                    f.write(";".join(rec) + "\n")
                    self._add_scenario_id(spath, id)
                    id += 1
            with open("/tmp/1.csv", "r") as f:
                cursor = connection.cursor()
                cursor.copy_from(f, "salts_scenario", sep=";")
        for spath in self.get_scenario_pathes('D'):
            if spath in scenario_pathes:
                self.set_scenario_status(spath, 'A')
        for spath in self.get_scenario_pathes('A'):
            if spath not in scenario_pathes:
                self.set_scenario_status(spath, 'D')


def getIniManager(lt_path):
    return IniCtrl(lt_path)

ini_manager = getIniManager(LT_PATH)
