import argparse
import csv
import json
import logging.config
import os
from typing import TextIO
# import config as cn
import re

if __package__ == 'scripts':
    import scripts.config as cn
else:
    import config as cn

class CallableDict(dict):
    def __getitem__(self, key):
        val = super().__getitem__(key)
        if callable(val):
            return val()
        return val


class MandatoryFieldException(Exception):
    pass


class TooManyFieldException(Exception):
    pass


class RetentionPeriodOutOfRange(Exception):
    pass


class InvalidURL(Exception):
    pass


class InvalidAccountName(Exception):
    pass


currentPath = os.path.abspath(os.getcwd())
log_config_path = '{}/utils/logging.json'.format(currentPath)


def setup_logging(default_path=cn.log_config_path, default_level=logging.INFO, env_key='LOG_CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        f: TextIO
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def getLogDir(log_file_name):
    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
    log_fname = os.path.join(log_dir, log_file_name + '.log')
    return log_fname


def paramRead():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', nargs=1,
                        help='JSON or CSV file to be processed',
                        type=argparse.FileType('r'))
    return parser.parse_args()


logger = setup_logging()
logger = logging.getLogger(__name__)


def csvToJson(input_csv):
    accountDict = {"account": {}, "data_platform": {}}
    if (check_line_count(input_csv) != 2):
        logger.error("Multiple/Incomplete Lines not allowed ")
        return accountDict
    try:
        with open(input_csv) as f:
            readRecs = csv.reader(f, delimiter=',')
            csvHeader = list(next(readRecs))
            for row in readRecs:
                retAction = whichActionType(row)
                retCheck = check_fields(retAction, csvHeader)
                rowDict = listToDict(csvHeader, row)
                if (retAction in cn.valid_quick_actions):
                    logger.info(f"Action type ->  {retAction}")
                    accountDict['account']['account_uid'] = rowDict.get('account_uid')
                    accountDict['account']['account_name'] = rowDict.get('account_name')  # None'
                    accountDict['data_platform']['action_type'] = retAction
                elif (retAction == 'ENABLE-DUAL-SEND-MODE'):
                    if (checkIfUrlValid(rowDict.get('es_alt_endpoint_url')) == True and checkIfUrlValid( rowDict.get('kbn_alt_endpoint_url'))==True ):
                        accountDict['account']['account_uid'] = rowDict.get('account_uid')
                        accountDict['data_platform']['action_type'] = retAction
                        accountDict['data_platform']['es_alt_endpoint_url'] = rowDict.get('es_alt_endpoint_url')
                        accountDict['data_platform']['kbn_alt_endpoint_url'] = rowDict.get('kbn_alt_endpoint_url')
                    else:
                        raise InvalidURL(
                            f"Invalid URL {rowDict.get('es_alt_endpoint_url')} or {rowDict.get('kbn_alt_endpoint_url')} ")

                elif (retAction == 'UPDATE-RETENTION-PERIOD'):
                    if (validRetentionPeriod(int(rowDict.get('retention_period'))) == False):
                        raise RetentionPeriodOutOfRange(
                            f'Valid Range: {cn.MIN_RETENTION_PERIOD} to {cn.MAX_RETENTION_PERIOD}')
                    else:
                        accountDict['account']['account_uid'] = rowDict.get('account_uid')
                        accountDict['data_platform']['action_type'] = retAction
                        accountDict['data_platform']['retention_period'] = rowDict.get('retention_period')

                elif (retAction == 'UPDATE'):
                    recValid = True
                    if (rowDict.get('es_endpoint_url') is not None or rowDict.get('kbn_endpoint_url')):
                        if (checkIfUrlValid(rowDict.get('es_endpoint_url')) == False):
                            raise InvalidURL(
                                f"Invalid URL {rowDict.get('es_endpoint_url')} or {rowDict.get('kbn_endpoint_url')}")
                            recValid = False
                    if (int(len(rowDict.get('account_name')) > cn.MAX_NAME_LENGTH) or int(len(rowDict.get('account_name'))) < 1 ):
                        raise InvalidAccountName(f"Account Name Error :  exceeds {cn.MAX_NAME_LENGTH} chars or Empty! ")
                        recValid = False
                    if recValid:
                        accountDict['account']['account_uid'] = rowDict.get('account_uid')
                        accountDict['account']['account_name'] = rowDict.get('account_name')
                        accountDict['data_platform']['action_type'] = rowDict.get('action_type')
                        accountDict['data_platform']['account_enabled'] = str_to_bool(rowDict.get('account_enabled'))
                        accountDict['data_platform']['es_endpoint_url'] = rowDict.get('es_endpoint_url')
                        accountDict['data_platform']['es_alt_endpoint_url'] = rowDict.get('es_alt_endpoint_url')
                        accountDict['data_platform']['kbn_endpoint_url'] = rowDict.get('kbn_endpoint_url')
                        accountDict['data_platform']['kbn_alt_endpoint_url'] = rowDict.get('kbn_alt_endpoint_url')
                        accountDict['data_platform']['description'] = rowDict.get('description')
                elif (retAction == 'NEW'):
                    recValid = True
                    if ( checkIfUrlValid( rowDict.get('es_endpoint_url') )==False or checkIfUrlValid( rowDict.get('kbn_endpoint_url'))==False ):
                        raise InvalidURL(
                            f"Invalid URL {rowDict.get('es_endpoint_url')} or {rowDict.get('kbn_endpoint_url')}")
                        recValid=False
                    if (rowDict.get('es_endpoint_url') is not None or rowDict.get('kbn_endpoint_url')):
                        if (checkIfUrlValid(rowDict.get('es_endpoint_url')) == False):
                            raise InvalidURL(
                                f"Invalid URL {rowDict.get('es_endpoint_url')} or {rowDict.get('kbn_endpoint_url')}")
                            recValid = False
                    if (rowDict.get('es_alt_endpoint_url') is not None and rowDict.get('es_endpoint_url') is None):
                        recValid = False
                    if (rowDict.get('kbn_alt_endpoint_url') is not None and rowDict.get('kbn_endpoint_url') is None):
                        recValid = False
                    if ( int(len(rowDict.get('account_name')) > cn.MAX_NAME_LENGTH) or int(len(rowDict.get('account_name')))<1):
                        raise InvalidAccountName(f"Account Name Error:  exceeds {cn.MAX_NAME_LENGTH} chars or Empty!")
                        recValid = False
                    if recValid:
                        accountDict['account']['account_uid'] = rowDict.get('account_uid')
                        accountDict['account']['account_name'] = rowDict.get('account_name')
                        accountDict['data_platform']['action_type'] = rowDict.get('action_type')
                        accountDict['data_platform']['account_enabled'] = str_to_bool(rowDict.get('account_enabled'))
                        accountDict['data_platform']['es_endpoint_url'] = rowDict.get('es_endpoint_url')
                        accountDict['data_platform']['es_alt_endpoint_url'] = rowDict.get('es_alt_endpoint_url')
                        accountDict['data_platform']['kbn_endpoint_url'] = rowDict.get('kbn_endpoint_url')
                        accountDict['data_platform']['kbn_alt_endpoint_url'] = rowDict.get('kbn_alt_endpoint_url')
                        accountDict['data_platform']['last_known_good_enabled'] = str_to_bool(
                            rowDict.get('last_known_good_enabled'))
                        accountDict['data_platform']['dual_send_enabled'] = str_to_bool(
                            rowDict.get('dual_send_enabled'))
                        accountDict['data_platform']['description'] = rowDict.get('description')
                        accountDict['data_platform']['retention_period'] = (
                            0 if rowDict.get('retention_period') == 'None' or
                                 rowDict.get('retention_period') is None else
                            int(rowDict.get('retention_period'))
                        )
                        accountDict['data_platform']['index_rollover_policy_max_doc_count'] = (
                            0 if rowDict.get('index_rollover_policy_max_doc_count') == 'None' or
                                 rowDict.get('index_rollover_policy_max_doc_count') is None or
                                 len(rowDict.get('index_rollover_policy_max_doc_count')) == 0 else
                            int(rowDict.get('index_rollover_policy_max_doc_count')))
                        accountDict['data_platform']['index_rollover_policy_max_age_days'] = (
                            0 if rowDict.get('index_rollover_policy_max_age_days') == 'None' or
                                 rowDict.get('index_rollover_policy_max_age_days') is None or
                                 len(rowDict.get('index_rollover_policy_max_age_days')) == 0 else
                            int(rowDict.get('index_rollover_policy_max_age_days')))
                        accountDict['data_platform']['etl_enabled'] = str_to_bool(rowDict.get('etl_enabled'))

    except Exception as e:
        logger.error(f"Opening CSV File, Exception occurred {e}", exc_info=True)
    return accountDict


def whichActionType(recInput):
    action_found = []
    retRes = ""
    valid_actions = cn.valid_action_types
    newList = list(map(lambda x: x.upper(), recInput))
    # should appear only once to be valid
    for y in valid_actions:
        if newList.count(y) == 1:
            action_found.append(y)

    if (len(action_found) == 1):
        # valid action, only appeared once, can add more validations here
        retRes = retRes.join(action_found)
    else:
        retRes = 'Invalid Action Type'
    return retRes


def listToDict(csvHeader, row):
    updateDict = {}
    if (len(csvHeader) == len(row)):
        for y in range(0, len(csvHeader)):
            updateDict[csvHeader[y]] = row[y]
    else:
        logger.error("Number of headers not equal to values!")
    return updateDict


def str_to_bool(s):
    if type(s) == 'String' or type(s) == str:
        if s.upper() == 'TRUE':
            return True
        elif s.upper() == 'FALSE':
            return False
    elif type(s) == bool:
        return s
    else:
        # goes to default value
        return None


def check_file_type(f):
    if type(f) != 'NoneType':
        filetype = f.name[f.name.rfind("."):len(f.name)].upper()
        return filetype


def check_line_count(input_csv):
    with open(input_csv) as f:
        fileRecs = csv.reader(f, delimiter=',')
        row_count = sum(1 for row in fileRecs)
    return row_count


def check_fields(action_type, inputData):
    result = 'passed'
    check_mandatory = False
    cn.mod_account_required_fields.sort()
    cn.dual_send_mode_required_fields.sort()
    cn.retention_period_required_fields.sort()
    check_noexpose = any(item in cn.no_exposure_fields for item in inputData)
    logger.info(f'action type -> {action_type.upper()}')
    if check_noexpose is True:
        raise TooManyFieldException(f'Entries not required: {cn.no_exposure_fields}')
    logger.info('check mandatory fields')
    if (action_type.upper() == 'NEW'):
        check_mandatory = all(item in inputData for item in cn.new_account_required_fields)
        check_size = True
    elif (action_type.upper() == 'UPDATE'):
        check_mandatory = all(item in inputData for item in cn.mod_account_required_fields)
        check_size = any(item in inputData for item in cn.non_updatables)
        if check_size == True:
            check_size = False
        else:
            check_size = True
    elif (action_type.upper() in cn.valid_quick_actions):
        check_mandatory = all(item in inputData for item in cn.mod_account_required_fields)
        check_size = (inputData == cn.mod_account_required_fields)
    elif (action_type.upper() == 'ENABLE-DUAL-SEND-MODE'):
        check_mandatory = all(item in inputData for item in cn.dual_send_mode_required_fields)
        check_size = (inputData == cn.dual_send_mode_required_fields)
    elif (action_type.upper() == 'UPDATE-RETENTION-PERIOD'):
        check_mandatory = all(item in inputData for item in cn.retention_period_required_fields)
        check_size = (inputData == cn.retention_period_required_fields)
    else:
        print(action_type)

    if check_mandatory is True:
        print('all required fields found')
        if check_size is False:
            raise TooManyFieldException(f'There are entries not required!')
    else:
        raise MandatoryFieldException(
            f'Missing required fields: {cn.new_account_required_fields} for action: {action_type}')


# need to know which action types uses the check URL
def checkIfUrlValid(mstr_url):
    result = False
    if( len(mstr_url) > 0 ):
        regex = re.compile(
             r'^(?:http|ftp)s?://'  # http:// or https://
             r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
             r'localhost|'  # localhost...
             r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
             r'(?::\d+)?'  # optional port
             r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if (re.match(regex, mstr_url) is not None):
                   result = True
    return result

# valid :   http://www.example.com
# invalid : test.com, com, kibanaurl.com
# No Quote(s) in csv

# check_mandatory = all(item in inputData for item in cn.new_account_required_fields)
def check_not_empty( inputData, required_fields ):
    for x in inputData:
        print( x )
        if(  len(x) < 1 ):
            return False
    return True

# check length applies to both descriptions and url
def checkStringLength(inputKey, inputValue, valid_field_length):
    result = True
    if (len(inputValue) < 1):
        return 'False'
    else:
        correct_length = valid_field_length.get(inputKey)
        if (len(inputValue) > correct_length):
            return 'False'
    return result


def validRetentionPeriod(inputRetention):
    result = False
    if (inputRetention >= cn.MIN_RETENTION_PERIOD and inputRetention <= cn.MAX_RETENTION_PERIOD):
        result = True
    return result
