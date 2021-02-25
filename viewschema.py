import datetime,  logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, ARRAY, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class vAcctManagement(Base):
    __tablename__ = 'v_dp_account'
    account_uid = Column(String, primary_key=True )
    account_name = Column(String)
    account_enabled = Column(Boolean)
    retention_period = Column(Integer)
    es_endpoint_url = Column(String)
    es_alt_endpoint_url = Column(String)
    kbn_endpoint_url = Column(String)
    kbn_alt_endpoint_url = Column(String)
    last_known_good_enabled = Column(Boolean)
    dual_send_enabled = Column(Boolean)
    index_rollover_policy_max_doc_count = Column(Integer)
    index_rollover_policy_max_age_days = Column(Integer)
    account_deleted = Column(Boolean)
    action_type = Column(String)
    description = Column(String)
    updated_date = Column(String)
    etl_enabled = Column(Boolean)

