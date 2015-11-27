#!/bin/bash
cp ./process_expired.ini ./test_process_expired.ini
cp ./db_settings.ini ./test_db_settings.ini
rm -f ./*.copy
python test_process_expired.py
rm ./test_process_expired.ini
rm ./test_db_settings.ini

