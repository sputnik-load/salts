# -*- coding: utf-8 -*-
#
import argparse
import ConfigParser
import psycopg2
from itertools import combinations


DB_CONFIG="db_settings.ini"

def connect_db(args):
    config = ConfigParser.RawConfigParser()
    db_config = DB_CONFIG
    config.read(db_config)
    db_section_name = args.db_section
    if not config.has_section(db_section_name):
        raise Exception("Config %s file hasn't '%s' section." % (
                        db_config, db_section_name))

    db_settings = {"host": "", "user": "", "password": ""}
    for setting in db_settings:
        if not config.has_option(db_section_name, setting):
            raise Exception("Config %s file hasn't '%s' option in '%s' section." % (
                            db_config, db_section_name, setting))
        db_settings[setting] = config.get(db_section_name, setting)

    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
                    db_settings["host"], db_section_name,
                    db_settings["user"], db_settings["password"])
    return psycopg2.connect(conn_string)


def existed_types(conn):
    with conn.cursor() as cursor:
        query = "SELECT name_list FROM salts_generatortype \
ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        rec = cursor.fetchone()
        if not rec:
            return []
        return rec[0].split(",")


def generate_types(names, types=[]):
    length = len(names)
    if length > 1:
        types = generate_types(names[:length-1], types)
    comb = []
    for i in range(len(names)):
        comb += list(combinations(names, i+1))
    for t in types:
        if t in comb:
            comb.remove(t)
    types += comb
    return types


def generate_type(conn, id, name_list):
    with conn.cursor() as cursor:
        query = "SELECT name_list FROM salts_generatortype WHERE id=%d" % (id)
        cursor.execute(query)
        rec = cursor.fetchone()
        if rec:
            if rec[0] != name_list:
                query = "UPDATE salts_generatortype SET name_list='%s' where id=%d" % (name_list, id)
                cursor.execute(query)
                conn.commit()
                print "Record (id=%d, name_list=%s). Updated." % (id, name_list)
            else:
                print "Record (id=%d, name_list=%s). Existed." % (id, name_list)
        else:
            query = "INSERT INTO salts_generatortype (id, name_list) VALUES (%d, '%s')" % (id, name_list)
            cursor.execute(query)
            conn.commit()
            print "Record (id=%d, name_list=%s). Inserted." % (id, name_list)


def update_type_name(old_value, new_value):
    with conn.cursor() as cursor:
        query = "SELECT id FROM salts_generatortype WHERE \
name_list ~ '^{new_type}$|{new_type},|,{new_type}'".format(new_type=new_value)
        cursor.execute(query)
        rec = cursor.fetchone()
        if rec:
            print "%s type is existed already." % new_value
            return
        query = "UPDATE salts_generatortype SET name_list=OVERLAY( \
name_list PLACING '{new_type}' FROM POSITION ('{old_type}' in name_list) \
FOR CHAR_LENGTH('{old_type}')) WHERE \
name_list ~ '^{old_type}$|{old_type},|,{old_type}' RETURNING id".format(old_type=old_value,
                                                           new_type=new_value)
        cursor.execute(query)
        conn.commit()
        rec = cursor.fetchall()
        print "%d records were updated." % len(rec)


parser = argparse.ArgumentParser(description="Добавляет или переименовывает типы в базе.")
parser.add_argument("names", metavar="NAMES", nargs="+", help="Список")
parser.add_argument("--db-section", "-d", dest="db_section",
                    default="test_salts_db",
                    help="Имя секции в файле db_settings.ini (содержит настройки для подключения к базе).")
parser.add_argument("--add", "-a", action="store_const",
                    const=True, default=False,
                    help="Добавляет новые типы. Если тип существует, то он не добавляется.")
parser.add_argument("--rename", "-r", action="store_const",
                    const=True, default=False,
                    help="Переименовывает тип. Если тип не существует, то ничего не происходит.")
args = parser.parse_args()
conn = connect_db(args)
if args.add:
    e_types = existed_types(conn)
    for et in e_types:
        if et in args.names:
            args.names.remove(et)
    types = generate_types(e_types + args.names)
    generate_type(conn, 1, "unknown")
    id = 2
    for t in types:
        generate_type(conn, id, ",".join(t))
        id += 1
elif args.rename and len(args.names) == 2:
    update_type_name(args.names[0], args.names[1])
