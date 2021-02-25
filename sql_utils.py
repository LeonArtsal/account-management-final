import sqlalchemy
import sqlalchemy_utils
import logging.config, udf
import filereader as pr

logger = udf.setup_logging()
logger = logging.getLogger(__name__)


def if_db_exists( db=None):
    check_db = db if db is not None else db_name
    database_url = set_url_db( pr.postgres_endpoint, check_db)
    logger.debug("check database URL '{}'".format(database_url))
    try:
        if sqlalchemy_utils.database_exists(database_url):
            logger.debug("DB '{}' exists".format(check_db))
            return True
    except sqlalchemy.exc.NoSuchModuleError as me:
        logger.error("cannot check if database {} exists: {}".
                     format(check_db, me))
        raise osdbError("cannot handle {} dialect".
                        format(self.dialect)) from None

    logger.debug("DB does not exist")
    return False


