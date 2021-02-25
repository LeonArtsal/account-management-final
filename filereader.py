
class dpAccountRead:
    def __init__(self, account, data_platform):
        self.account_uid = account.get('account_uid')
        self.account_name = account.get('account_name')
        self.account_enabled = data_platform.get('account_enabled')
        self.action_type = data_platform.get('action_type')
        self.es_endpoint_url = data_platform.get('es_endpoint_url')
        self.es_alt_endpoint_url = data_platform.get('es_alt_endpoint_url')
        self.kbn_endpoint_url = data_platform.get('kbn_endpoint_url')
        self.kbn_alt_endpoint_url = data_platform.get('kbn_alt_endpoint_url')
        self.last_known_good_enabled = data_platform.get('last_known_good_enabled')
        self.dual_send_enabled = data_platform.get('dual_send_enabled')
        self.description = data_platform.get('description')
        self.retention_period = data_platform.get('retention_period')
        self.index_rollover_policy_max_doc_count = data_platform.get('index_rollover_policy_max_doc_count')
        self.etl_enabled = data_platform.get('etl_enabled')
        self.index_rollover_policy_max_age_days = data_platform.get('index_rollover_policy_max_age_days')


    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)

    def __repr__(self):
        return f'<dpAccountRead>{self.account_uid},{self.account_name}, {self.account_enabled},{self.action_type},' \
               f'{self.es_endpoint_url},{self.es_alt_endpoint_url}, {self.kbn_endpoint_url},{self.kbn_alt_endpoint_url},' \
               f'{self.last_known_good_enabled},{self.dual_send_enabled} {self.description}, {self.retention_period}, ' \
               f'{self.index_rollover_policy_max_doc_count}, {self.etl_enabled}, ' \
               f'{self.index_rollover_policy_max_age_days}>'


