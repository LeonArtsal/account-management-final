import os

currentPath = os.path.abspath(os.getcwd())
tbl_name = 'dp_account'
view_name = 'v_dp_account'
log_file_name = 'acct_mgmt_main'
log_config_path = '{}/utils/logging.json'.format(currentPath)
log_config_out = '{}/logs/'.format(currentPath)
input_csv = '{}/data/insertTemplate.csv'.format(currentPath)
testDataPath = '/tests/data'


# 13 action types
valid_action_types = {'NEW', 'UPDATE', 'DELETE', 'UNDELETE', 'ENABLE-ACCOUNT', 'DISABLE-ACCOUNT',
                      'ENABLE-DUAL-SEND-MODE', 'ENABLE-ETL', 'DISABLE-ETL',
                      'DISABLE-DUAL-SEND-MODE', 'ENABLE-LAST-KNOWN-GOOD-MODE', 'DISABLE-LAST-KNOWN-GOOD-MODE',
                      'UPDATE-RETENTION-PERIOD'}

valid_quick_actions = {'DELETE', 'UNDELETE', 'ENABLE-ACCOUNT', 'DISABLE-ACCOUNT', 'ENABLE-ETL', 'DISABLE-ETL',
                       'DISABLE-DUAL-SEND-MODE', 'ENABLE-LAST-KNOWN-GOOD-MODE', 'DISABLE-LAST-KNOWN-GOOD-MODE'}

basic_actions =['NEW','UPDATE','DELETE','UNDELETE','UPDATE-RETENTION-PERIOD']

enable_actions = {'ENABLE-ACCOUNT',
                  'ENABLE-DUAL-SEND-MODE',
                  'ENABLE-LAST-KNOWN-GOOD-MODE',
                  'ENABLE-ETL'}

disable_actions = {'DISABLE-ACCOUNT',
                   'DISABLE-DUAL-SEND-MODE',
                   'DISABLE-LAST-KNOWN-GOOD-MODE',
                   'DISABLE-ETL'}

new_account_required_fields = ['account_uid', 'account_name',
                               'es_endpoint_url',
                               'kbn_endpoint_url',
                               'action_type',
                               'description']

no_exposure_fields = ['index_rollover_policy_max_age_days', 'index_rollover_policy_max_doc_count']

update_required_fields = ['account_uid',
                          'es_endpoint_url', 'es_alt_endpoint_url', 'kbn_endpoint_url',
                          'kbn_alt_endpoint_url',
                          'last_known_good_enabled', 'dual_send_enabled']
mod_account_required_fields = ['account_uid', 'action_type']
retention_period_required_fields = ['account_uid', 'action_type', 'retention_period']
dual_send_mode_required_fields = ['account_uid', 'action_type', 'es_alt_endpoint_url', 'kbn_alt_endpoint_url']
non_updatables = ['retention_period', 'account_enabled', 'etl_enabled', 'dual_send_enabled', 'last_known_good_enabled']

# added string and retention validations
MAX_RETENTION_PERIOD = 180
MIN_RETENTION_PERIOD = 7
MAX_NAME_LENGTH=512
MAX_DESCRIPTION=512

# PYTEST config

jPath = f'{currentPath}/{testDataPath}/testData1.json'
jNewAccount = '{}/tests/data/testData1.json'.format(currentPath)
jUpdAccount = '{}/tests/data/testData2.json'.format(currentPath)
jDelAccount = '{}/tests/data/testData3.json'.format(currentPath)
#  csv test files location
csv_new = f'{currentPath}/{testDataPath}/testData_new.csv'
csv_update = f'{currentPath}/{testDataPath}/testData_update.csv'
csv_delete = f'{currentPath}/{testDataPath}/testData_delete.csv'
csv_undelete = f'{currentPath}/{testDataPath}/testData_undelete.csv'
csv_enableaccount = f'{currentPath}/{testDataPath}/testData_enableaccount.csv'
csv_disableaccount = f'{currentPath}/{testDataPath}/testData_disableaccount.csv'
csv_enable_etl = f'{currentPath}/{testDataPath}/testData_enable_etl.csv'
csv_disable_etl = f'{currentPath}/{testDataPath}/testData_disable_etl.csv'
csv_enable_dualmode = f'{currentPath}/{testDataPath}/testData_enabledualsendmode.csv'
csv_disable_dualmode = f'{currentPath}/{testDataPath}/testData_disabledualsendmode.csv'
csv_update_retention = f'{currentPath}/{testDataPath}/testData_update_retention.csv'

jAccount = ['account_uid', 'account_name']
jPlatForm = ['action_type', 'account_enabled', 'es_endpoint_url',
             'es_alt_endpoint_url', 'kbn_endpoint_url', 'kbn_alt_endpoint_url',
             'last_known_good_enabled', 'dual_send_enabled', 'description',
             'retention_period', 'index_rollover_policy_max_doc_count',
             'index_rollover_policy_max_age_days', 'etl_enabled']
