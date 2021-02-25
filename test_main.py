import json
import os.path
import pytest
import sqlalchemy_utils
import sys
from scripts import udf
from scripts import config as tcn
import tests.test_functions as db
from scripts import env_vars as env_vars
#from scripts import config as cn

def readJson(fileLoc):
    with open(fileLoc) as f:
        data = json.load(f)
    return data

db.create_db_tables_if_not_exists()
mDictFile = readJson(tcn.jPath)

#  to check on json or csv
#  if both files present -- pass,  if both files absent failed
#  if one of the file is present - pass

@pytest.mark.parametrize(
    "test_input,expected",
    [(str(len(mDictFile)), 2)]
    # i, ( str(mDictFile['data_platform']['action_type']), str('New')) ]
)
# check parameters
def test_param_head_count(test_input, expected):
    assert eval(test_input) == expected


def test_python_version():
    assert (sys.version_info[0] >= 3)


# check database if exists
def test_database_if_exist():
    assert (sqlalchemy_utils.functions.database_exists(env_vars.postgres_endpoint) == True)


# check if action type is correct/valid

def test_action_type():
    assert (mDictFile['data_platform']['action_type'].upper() in
            tcn.valid_action_types)


testDataPath = '/tests/data/'
currentPath = os.path.abspath(os.getcwd()) + testDataPath
csv_new = '{}testData_new.csv'.format(currentPath)


#  Read the json's

newAccount = readJson(tcn.jNewAccount)
updAccount = readJson(tcn.jUpdAccount)
delAccount = readJson(tcn.jDelAccount)

# Read the CSV's

newAccountCsv = udf.csvToJson(tcn.csv_new)
updAccountCsv = udf.csvToJson(tcn.csv_update)
delAccountCsv = udf.csvToJson(tcn.csv_delete)
undelAccountCsv = udf.csvToJson(tcn.csv_undelete)
enableAccountCsv = udf.csvToJson(tcn.csv_enableaccount)
disableAccountCsv = udf.csvToJson(tcn.csv_disableaccount)
enableEtlCsv = udf.csvToJson(tcn.csv_enable_etl)
disableEtlCsv = udf.csvToJson(tcn.csv_disable_etl)
enableDualModeCsv = udf.csvToJson(tcn.csv_enable_dualmode)
disableDualModeCsv = udf.csvToJson(tcn.csv_disable_dualmode)
updateRetentionCsv = udf.csvToJson(tcn.csv_update_retention)

# Test Functions ..

def test_csv_add_record():
    assert (db.new_crecord(newAccountCsv) == 'Record Inserted')

def test_csv_update_record():
    assert (db.update_a_crecord(updAccountCsv) == "Record Updated")


def test_csv_duplicate_record():
    assert (db.duplicate_a_crecord(newAccountCsv) == "Record Duplicated")

def test_csv_enable_account():
    assert (db.enable_field(enableAccountCsv) == "Account Enabled")

def test_csv_disable_account():
    assert (db.disable_field(disableAccountCsv) == "Account Disabled")

def test_csv_enable_etl():
    assert (db.enable_field(enableEtlCsv) == "ETL Enabled")


def test_csv_disable_etl():
    assert (db.disable_field(disableEtlCsv) == "ETL Disabled")

def test_csv_enable_dual_send():
    assert (db.enable_field(enableDualModeCsv) == "Dual Send Enabled")

def test_csv_disable_dual_send():
    assert (db.disable_field(disableDualModeCsv) == 'Dual Send Disabled')

def test_csv_retention_period():
    assert (db.update_retention(updateRetentionCsv) == 'Retention Updated')

def test_csv_delete_record():
    assert (db.delete_a_crecord(delAccountCsv) == "Record Deleted")

def test_json_add_record():
    assert (db.new_jrecord(newAccount) == "Record Inserted")

def test_json_update_record():
    assert (db.update_a_jrecord(updAccount) == "Record Updated")

def test_json_duplicate_record():
    assert (db.duplicate_a_jrecord(newAccount) == "Record Duplicated")

def test_json_delete_record():
    assert (db.delete_a_jrecord(delAccount) == "Record Deleted")
