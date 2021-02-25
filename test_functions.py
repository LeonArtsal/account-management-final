import logging

import sqlalchemy_utils
from scripts import udf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import scripts.env_vars as env_vars
from scripts import config
from scripts.models import models as db

logger = udf.setup_logging()
logger = logging.getLogger(__name__)

engine = create_engine(env_vars.postgres_endpoint)

if not sqlalchemy_utils.functions.database_exists(env_vars.postgres_endpoint):
    sqlalchemy_utils.functions.create_database(env_vars.postgres_endpoint)

def create_db_tables_if_not_exists():
    if sqlalchemy_utils.functions.database_exists(env_vars.postgres_endpoint):
            if not engine.dialect.has_table(engine, config.tbl_name):
                db.Base.metadata.create_all(bind=engine)

def new_crecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    reSult = ""
    try:
         dpMast = db.dpMaster()
         dpDet = db.dpDetails()
         dpMast.account_uid = account['account']['account_uid']
         dpMast.account_name = account['account']['account_name']
         dpDet.account_uid = account['account']['account_uid']
         dpDet.action_type = account['data_platform']['action_type']
         dpDet.es_endpoint_url = account['data_platform']['es_endpoint_url']
         dpDet.kbn_endpoint_url = account['data_platform']['kbn_endpoint_url']
         dpDet.description = account['data_platform']['description']
         session.add(dpMast)
         session.add(dpDet)
         session.commit()
    except Exception as e:
        reSult = f"Insert Failed {e}"
    else:
        reSult = "Record Inserted"
    return reSult


def update_a_crecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    account_uid = account['account']['account_uid']
    result=""
    try:
        tblRecord = session.query(db.dpMaster).get(account_uid)
        if tblRecord is not None:
            tblRecord.account_name = account['account']['account_name']
            session.commit()
    except Exception as e:
         result = e
    else:
         result = "Record Updated"
    return result


def update_a_crecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    result='Failed'
    account_uid = account['account']['account_uid']
    account_name = account['account']['account_name']
    try:
        tblRecord = session.query(db.dpMaster).get(account_uid)
        if tblRecord is not None:
            result='Record Updated'
        else:
            result='Record Not Found'
            logger.error(f"Account UID not found -> {account_uid}")

    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=True)
    return result

def duplicate_a_crecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    reSult = ""
    dpMast = db.dpMaster()
    dpMast.account_uid = account['account']['account_uid']
    try:
        session.add(dpMast)
        session.commit()
    except Exception as e:
        reSult ="Record Duplicated"
    else:
        reSult = "Record Inserted"
    return reSult

def delete_a_crecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    reSult=""
    try:
        recMas = session.query(db.dpMaster).filter_by(account_uid=account['account']['account_uid']).delete()
        recDet = session.query(db.dpDetails).filter_by(account_uid=account['account']['account_uid']).delete()
        session.commit()
    except Exception as e:
        reSult="Record not Deleted"
    else:
        reSult="Record Deleted"
    return reSult

def enable_field(csvAccount):
    Session = sessionmaker(bind=engine)
    session = Session()
    result=""
    account_uid = csvAccount['account']['account_uid']
    action_type = csvAccount['data_platform']['action_type']
    try:
        tblRecord = session.query(db.dpMaster).get( account_uid )
        if tblRecord.account_name is not None:
            dpDet = db.dpDetails()
            dpDet.account_uid = account_uid
            dpDet.action_type = action_type
            if action_type.upper() == 'ENABLE-ACCOUNT':
                result='Account Enabled'
            elif action_type.upper() == 'ENABLE-DUAL-SEND-MODE':
                result='Dual Send Enabled'
            elif action_type.upper() == 'ENABLE-LAST-KNOWN-GOOD-MODE':
                result='Last Known Good Enabled'
            elif action_type.upper()=='ENABLE-ETL':
                result='ETL Enabled'
            else:
                result='Unknown type'
    except Exception as e:
        print( e )
    return result

def disable_field(csvAccount):
    Session = sessionmaker(bind=engine)
    session = Session()
    result=""
    print( csvAccount )
    account_uid = csvAccount['account']['account_uid']
    action_type = csvAccount['data_platform']['action_type']
    try:
        tblRecord = session.query(db.dpMaster).get( account_uid )
        if tblRecord.account_name is not None:
            dpDet = db.dpDetails()
            dpDet.account_uid = account_uid
            dpDet.action_type = action_type
            if action_type.upper() == 'DISABLE-ACCOUNT':
                result='Account Disabled'
            elif action_type.upper() == 'DISABLE-DUAL-SEND-MODE':
                result='Dual Send Disabled'
            elif action_type.upper() == 'DISABLE-LAST-KNOWN-GOOD-MODE':
                result='Last Known Good Enabled'
            elif action_type.upper()=='DISABLE-ETL':
                result='ETL Disabled'
            else:
                result='Unknown type'
    except Exception as e:
        print( e )
    return result

def update_retention(csvRetention):
    Session = sessionmaker(bind=engine)
    session = Session()
    result = 'Failed'
    account_uid = csvRetention['account']['account_uid']
    try:
        tblRecord = session.query(db.dpMaster).get(account_uid)
        resMessage = account_uid
        if tblRecord is not None:
            logger.info(f"Account UID -> {resMessage} .. Retention Period Updated!")
            result = 'Retention Updated'
        else:
            logger.error(f"Account UID not found -> {account_uid}")

    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=True)
    return result

def new_jrecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    reSult = ""
    # determine action type .. add, edit or disable
    dpMast = db.dpMaster()
    dpDet = db.dpDetails()
    dpMast.account_uid = account['account']['account_uid']
    dpMast.account_name = account['account']['account_name']
    dpDet.account_uid = account['account']['account_uid']
    dpDet.action_type = account['data_platform']['action_type']
    dpDet.es_endpoint_url = account['data_platform']['es_endpoint_url']
    dpDet.kbn_endpoint_url = account['data_platform']['kbn_endpoint_url']
    dpDet.description = account['data_platform']['description']
    try:
        session.add(dpMast)
        session.add(dpDet)
        session.commit()
    except Exception as e:
        reSult = f"Insert Failed {e}"
    else:
        reSult = "Record Inserted"
    return reSult


def update_a_jrecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    result=""
    try:
        tblRecord = session.query(db.dpMaster).get(account['account']['account_uid'])
        resMessage = "No record found!"
        if tblRecord is not None:
            tblRecord.account_name = account['account']['account_name']
            session.commit()
    except Exception as e:
         result = e
    else:
         result = "Record Updated"
    return result



def duplicate_a_jrecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    reSult = ""
    dpMast = db.dpMaster()
    dpMast.account_uid = account['account']['account_uid']
    try:
        session.add(dpMast)
        session.commit()
    except Exception as e:
        reSult ="Record Duplicated"
    else:
        reSult = "Record Inserted"
    return reSult


def delete_a_jrecord(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    reSult=""
    try:
        recMas = session.query(db.dpMaster).filter_by(account_uid=account['account']['account_uid']).delete()
        recDet = session.query(db.dpDetails).filter_by(account_uid=account['account']['account_uid']).delete()
        session.commit()
    except Exception as e:
        reSult="Record not Deleted"
    else:
        reSult="Record Deleted"
    return reSult

