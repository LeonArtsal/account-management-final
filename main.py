from typing import Any
import json, logging, csv, sys
import config as cn
import udf as udf

from models import models as db
import env_vars
import viewschema as vw
import sqlalchemy_utils
from sqlalchemy_utils import create_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from filereader import dpAccountRead
import logging.config
from io import StringIO
import boto3

# can't see the udf by scripts package
#from common import udf as udf # setup_logging
import udf

engine = create_engine(env_vars.postgres_endpoint)
logger = udf.setup_logging()
logger = logging.getLogger(__name__)


def create_view_if_not_exists():
    if not sqlalchemy_utils.functions.database_exists(env_vars.postgres_endpoint):
        logger.error('Database not found!!')
    try:
        # if not engine.dialect.has_table(engine, cn.tbl_name):
        if not engine.dialect.has_table(engine, cn.view_name):
            db.Base.metadata.create_all(bind=engine)
            create_db_view(engine)
        else:
            logger.info('View Exists!!')
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    else:
        logger.info('tables/verified')


def create_records(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    create_view_if_not_exists()
    changed_capture = False
    dpMast = db.dpMaster()
    dpDet = db.dpDetails()
    dpMast.account_uid = account.account_uid
    dpMast.account_name = account.account_name
    dpDet.account_uid = account.account_uid
    dpDet.account_enabled = (None if account.account_enabled is None else udf.str_to_bool( account.account_enabled))
    dpDet.action_type = account.action_type
    dpDet.es_endpoint_url = account.es_endpoint_url
    dpDet.es_alt_endpoint_url = account.es_alt_endpoint_url
    dpDet.retention_period = (None if account.retention_period == 0 else account.retention_period)
    dpDet.kbn_endpoint_url = account.kbn_endpoint_url
    dpDet.kbn_alt_endpoint_url = account.kbn_alt_endpoint_url
    dpDet.last_known_good_enabled = account.last_known_good_enabled
    dpDet.dual_send_enabled = account.dual_send_enabled
    dpDet.description = account.description
    dpDet.etl_enabled = udf.str_to_bool("True") if account.etl_enabled is None else udf.str_to_bool(
        account.etl_enabled)
    try:
        session.add(dpMast)
        session.add(dpDet)
        session.commit()
        changed_capture = True
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    else:
        logger.info('Account record added: {}'.format(dpMast.account_uid))
    return changed_capture

def update_records(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    changed_capture = False
    try:
        tblRecord = session.query(db.dpMaster).get(account.account_uid)
        dtlRecord = session.query(vw.vAcctManagement).get(account.account_uid)
        # generic update can only modify columns that are not covered by other action_types e.g. account_name, urls
        resMessage = account.account_uid
        if tblRecord is not None:
            tblRecord.account_name = tblRecord.account_name if account.account_name is None else account.account_name
            dpDet = db.dpDetails()
            dpDet.account_uid = account.account_uid
            if (account.account_enabled is None):
                dpDet.account_enabled = udf.str_to_bool(dtlRecord.account_enabled)
            else:
                dpDet.account_enabled = udf.str_to_bool(account.account_enabled)
            dpDet.action_type = account.action_type
            dpDet.es_endpoint_url = dtlRecord.es_endpoint_url if account.es_endpoint_url is None else account.es_endpoint_url
            dpDet.es_alt_endpoint_url = dtlRecord.es_alt_endpoint_url if account.es_alt_endpoint_url is None else account.es_alt_endpoint_url
            dpDet.retention_period =  dtlRecord.retention_period
            dpDet.kbn_endpoint_url = dtlRecord.kbn_endpoint_url if account.kbn_endpoint_url is None else account.kbn_endpoint_url
            dpDet.kbn_alt_endpoint_url = dtlRecord.kbn_alt_endpoint_url if account.kbn_alt_endpoint_url == None else account.kbn_alt_endpoint_url
            dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
            dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
            dpDet.description = dtlRecord.description if account.description is None else account.description
            dpDet.etl_enabled = dtlRecord.etl_enabled
            session.add(dpDet)
            session.commit()
            logger.info(f"Account UID -> {resMessage} .. Record Updated!")
            changed_capture = True
        else:
            logger.error(f"Account UID not found -> {account.account_uid}")

    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    return changed_capture

# soft delete
def delete_record(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    changed_capture = False
    try:
        tblRecord = session.query(db.dpMaster).get(account.account_uid)
        resMessage = account.account_uid
        if tblRecord is not None:
            tblRecord.account_deleted = True
            session.commit()
            logger.info(f"Account UID -> {resMessage} .. Record Deleted!")
            changed_capture = True
        else:
            logger.error(f"Account UID not found -> {account.account_uid}")
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    return changed_capture


def undelete_record(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    changed_capture = False
    try:
        tblRecord = session.query(db.dpMaster).get(account.account_uid)
        resMessage = account.account_uid
        if tblRecord is not None:
            tblRecord.account_deleted = False
            session.commit()
            logger.info(f"Account UID -> {resMessage} .. Record Restored (Undelete)")
            changed_capture = True
        else:
            logger.error(f"Account UID not found -> {account.account_uid}")
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    return changed_capture


def update_retention_period(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    changed_capture = False
    try:
        tblRecord = session.query(db.dpMaster).get(account.account_uid)
        dtlRecord = session.query(vw.vAcctManagement).get(account.account_uid)
        resMessage = account.account_uid
        if tblRecord is not None:
            dpDet = db.dpDetails()
            dpDet.account_uid = account.account_uid
            dpDet.account_enabled = dtlRecord.account_enabled
            dpDet.action_type = account.action_type
            dpDet.es_endpoint_url = dtlRecord.es_endpoint_url
            dpDet.es_alt_endpoint_url = dtlRecord.es_alt_endpoint_url
            dpDet.retention_period = account.retention_period
            dpDet.kbn_endpoint_url = dtlRecord.kbn_endpoint_url
            dpDet.kbn_alt_endpoint_url = dtlRecord.kbn_alt_endpoint_url
            dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
            dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
            dpDet.etl_enabled = dtlRecord.etl_enabled
            dpDet.description = 'Retention Period Update'
            session.add(dpDet)
            session.commit()
            logger.info(f"Account UID -> {resMessage} .. Retention Period Updated!")
            changed_capture = True
        else:
            logger.error(f"Account UID not found -> {account.account_uid}")

    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    return changed_capture


def disable_field(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    changed_capture = False
    try:
        tblRecord = session.query(db.dpMaster).get(account.account_uid)
        dtlRecord = session.query(vw.vAcctManagement).get(account.account_uid)
        resMessage = account.account_uid
        if tblRecord is not None:
            dpDet = db.dpDetails()
            dpDet.account_uid = account.account_uid
            dpDet.action_type = account.action_type

            if account.action_type.upper() == 'DISABLE-ACCOUNT':
                dpDet.account_enabled = udf.str_to_bool('FALSE')
                dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
                dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
                dpDet.etl_enabled = dtlRecord.etl_enabled
            elif account.action_type.upper() == 'DISABLE-DUAL-SEND-MODE':
                dpDet.dual_send_enabled = udf.str_to_bool('FALSE')
                dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
                dpDet.account_enabled = dtlRecord.account_enabled
                dpDet.etl_enabled = dtlRecord.etl_enabled
            elif account.action_type.upper() == 'DISABLE-LAST-KNOWN-GOOD-MODE':
                dpDet.last_known_good_enabled = udf.str_to_bool('FALSE')
                dpDet.account_enabled = dtlRecord.account_enabled
                dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
                dpDet.etl_enabled = dtlRecord.etl_enabled
            elif account.action_type.upper() == 'DISABLE-ETL':
                dpDet.etl_enabled = udf.str_to_bool('FALSE')
                dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
                dpDet.account_enabled = dtlRecord.account_enabled
                dpDet.dual_send_enabled = dtlRecord.dual_send_enabled

            dpDet.es_endpoint_url = dtlRecord.es_endpoint_url
            dpDet.es_alt_endpoint_url = dtlRecord.es_alt_endpoint_url
            dpDet.retention_period = dtlRecord.retention_period
            dpDet.kbn_endpoint_url = dtlRecord.kbn_endpoint_url
            dpDet.kbn_alt_endpoint_url = dtlRecord.kbn_alt_endpoint_url
            dpDet.description = f'DISABLED - {account.action_type}'
            session.add(dpDet)
            session.commit()
            logger.info(f"Account UID -> {resMessage} .. {account.action_type} Disabled!")
            changed_capture = True
        else:
            logger.error(f"Account UID not found -> {account.account_uid}")

    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    return changed_capture


def enable_field(account):
    Session = sessionmaker(bind=engine)
    session = Session()
    changed_capture = False
    try:
        tblRecord = session.query(db.dpMaster).get(account.account_uid)
        dtlRecord = session.query(vw.vAcctManagement).get(account.account_uid)
        resMessage = account.account_uid
        if tblRecord is not None:
            dpDet = db.dpDetails()
            dpDet.account_uid = account.account_uid
            dpDet.action_type = account.action_type
            if account.action_type.upper() == 'ENABLE-ACCOUNT':
                dpDet.account_enabled = udf.str_to_bool('TRUE')
                dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
                dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
                dpDet.es_alt_endpoint_url = dtlRecord.es_alt_endpoint_url
                dpDet.kbn_alt_endpoint_url = dtlRecord.kbn_alt_endpoint_url
                dpDet.etl_enabled = dtlRecord.etl_enabled
            elif account.action_type.upper() == 'ENABLE-DUAL-SEND-MODE':
                dpDet.dual_send_enabled = udf.str_to_bool('TRUE')
                dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
                dpDet.es_alt_endpoint_url = account.es_alt_endpoint_url
                dpDet.kbn_alt_endpoint_url = account.kbn_alt_endpoint_url
                dpDet.account_enabled = udf.str_to_bool( dtlRecord.account_enabled )
                dpDet.etl_enabled = dtlRecord.etl_enabled
            elif account.action_type.upper() == 'ENABLE-LAST-KNOWN-GOOD-MODE':
                dpDet.last_known_good_enabled = udf.str_to_bool('TRUE')
                dpDet.account_enabled = dtlRecord.account_enabled
                dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
                dpDet.es_alt_endpoint_url = dtlRecord.es_alt_endpoint_url
                dpDet.kbn_alt_endpoint_url = dtlRecord.kbn_alt_endpoint_url
                dpDet.etl_enabled = dtlRecord.etl_enabled
            elif account.action_type.upper()=='ENABLE-ETL':
                dpDet.etl_enabled =udf.str_to_bool('TRUE')
                dpDet.last_known_good_enabled = dtlRecord.last_known_good_enabled
                dpDet.account_enabled = dtlRecord.account_enabled
                dpDet.dual_send_enabled = dtlRecord.dual_send_enabled
                dpDet.es_alt_endpoint_url = dtlRecord.es_alt_endpoint_url
                dpDet.kbn_alt_endpoint_url = dtlRecord.kbn_alt_endpoint_url

            dpDet.es_endpoint_url = dtlRecord.es_endpoint_url
            dpDet.retention_period = dtlRecord.retention_period
            dpDet.kbn_endpoint_url = dtlRecord.kbn_endpoint_url

            dpDet.description = f'ENABLED - {account.action_type}'
            session.add(dpDet)
            session.commit()
            logger.info(f"Account UID -> {resMessage} .. {account.action_type} Enabled!")
            changed_capture = True
        else:
            logger.error(f"Account UID not found -> {account.account_uid}")

    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)
    return changed_capture


def s3DumpsRefresh():
    Session = sessionmaker(bind=engine)
    session = Session()

    if env_vars.aws_profile_local:
        # for local testing, likely to have aws profile in ~/.aws
        logger.info(f'Creating aws session using profile: {env_vars.aws_profile_local}')
        s3Session = boto3.session.Session(profile_name=env_vars.aws_profile_local)
    else:
        # container service scenario
        logger.info('Creating aws session using key and secret')
        # logger.info(f'aws_access_key_id: {env_vars.aws_access_key_id}')
        # logger.info(f'aws_secret_access_key: {env_vars.aws_secret_access_key}')
        # logger.info(f'aws_region: {env_vars.aws_region}')
        s3Session = boto3.session.Session(
            aws_access_key_id=env_vars.aws_access_key_id,
            aws_secret_access_key=env_vars.aws_secret_access_key,
            region_name=env_vars.aws_region)

        if env_vars.aws_role_arn:  # if there is an explicit role arn, then use it to assume that role
            logger.info('AWS role arn is present. Switching to assume role and creating new session')
            temp_sts_session = s3Session.client('sts')  # aws security token service - sts
            assumed_role_obj = temp_sts_session.assume_role(RoleArn=env_vars.aws_role_arn,
                                                            RoleSessionName='mysession',
                                                            DurationSeconds=1800)
            session_token = assumed_role_obj['Credentials']['SessionToken']
            access_key_id = assumed_role_obj['Credentials']['AccessKeyId']
            secret_access_key = assumed_role_obj['Credentials']['SecretAccessKey']
            s3Session = boto3.session.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=env_vars.aws_region,
                aws_session_token=session_token)

    tblRecord = session.query(vw.vAcctManagement)
    accounts_list = []
    accounts_dict = {}

    for n in tblRecord:
        accounts_dict = {
            'account_uid': n.account_uid,
            'account_name': n.account_name,
            'account_enabled': n.account_enabled,
            'retention_period': n.retention_period,
            'es_endpoint_url': n.es_endpoint_url,
            'es_alt_endpoint_url': n.es_alt_endpoint_url,
            'kbn_endpoint_url': n.kbn_endpoint_url,
            'kbn_alt_endpoint_url': n.kbn_alt_endpoint_url,
            'last_known_good_enabled': n.last_known_good_enabled,
            'dual_send_enabled': n.dual_send_enabled,
            'etl_enabled': n.etl_enabled,
            'description': n.description}
        accounts_list.append(accounts_dict)
    try:
        accountsF = StringIO(json.dumps(accounts_list))
        result = [json.dumps(record) for record in json.load(accountsF)]
        ndFormatted = '\n'.join(result)
        s3 = s3Session.resource('s3')
        object = s3.Object(env_vars.bucket_name, env_vars.bucket_file_name)
        object.put(Body=ndFormatted)
        session.close()
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)


def main(account_json):
    dActionItems = udf.CallableDict(
        {'NEW': lambda: create_records(account),'UPDATE': lambda: update_records(account),
         'DELETE': lambda: delete_record(account),'UNDELETE': lambda: undelete_record(account),
         'UPDATE-RETENTION-PERIOD': lambda: update_retention_period(account)} )
    try:
        account = dpAccountRead.from_json(account_json)
        retResult = False
        if account:
            if( account.action_type.upper() in cn.basic_actions ):
                retResult = dActionItems[ account.action_type.upper() ]
            elif (account.action_type.upper() in cn.enable_actions):
                retResult = enable_field(account)
            elif (account.action_type.upper() in cn.disable_actions):
                retResult = disable_field(account)
            else:
                logger.error(f"Unknown action type! ->   {account.action_type}")
                return retResult
    except Exception as e:
        logger.error(f"Exception occurred {e}", exc_info=False)


if __name__ == '__main__':
    logger.info('Application Starts')
    arguments = udf.paramRead()
    changed_capture = False
    if arguments.infile is None:
        logger.error("No input file passed, ex:  python main.py --infile myfile.csv")
    else:
        fileType = udf.check_file_type(arguments.infile[0])
        logger.info(fileType)
        if fileType == '.CSV':
            try:
                inputJson = udf.csvToJson(arguments.infile[0].name)
                if (len(inputJson['account']) > 0):
                    changed_capture = main(inputJson)
            except Exception as e:
                logger.error(f"Exception occurred {e}", exc_info=False)
        elif fileType == '.JSON':
            try:
                account_json = json.load(arguments.infile[0])
                logger.info(f"Input Json Reads : {account_json}")
                changed_capture = main(account_json)
            except Exception as e:
                logger.error(f"Exception occurred {e}", exc_info=False)

    logger.info(f"Application ends ... ")
    if (changed_capture == True):
        logger.info("RDS Table query to ndJson push to S3 Bucket")
        s3DumpsRefresh()

#
# two ways to invoke :
# 1.  takes given path and read csv/txt file as input
# python main.py --infile path/svTemplate.csv
# 2.  takes an argument of path and json file
# python main.py --infile path/jsonTemplate.json
#  cat accounts.txt | jq -c '.[]' > accountsNDJSON.json

