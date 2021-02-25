import datetime,  logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, ARRAY, Sequence, DateTime, \
    PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

# Note :
# All timezone-aware dates and times are stored internally in UTC.
# They are converted to local time in the zone specified by the
# timezone configuration parameter before being displayed to the client.


#from alembic import op

# in ORM concept this is the Object Model going to inherit from

Base = declarative_base()

class dpMaster(Base):
    __tablename__ = 'dp_account'
    account_uid = Column(String(64), primary_key=True)
    account_name = Column(String(32), unique=True, nullable=False)
    account_deleted = Column(Boolean, default=False, nullable=False)
    created_date = Column(DateTime(timezone=True), default= datetime.datetime.utcnow, nullable=False)

class dpDetails(Base):
    __tablename__ = 'dp_transaction'
    action_type = Column(String(32), nullable=False)
    account_uid = Column(String(64), nullable=False)
    account_enabled = Column(Boolean, default=True, nullable=False)
    description = Column(String(512))
    dual_send_enabled=Column(Boolean, default=False, nullable=False)
    etl_enabled = Column(Boolean, default=True, nullable=False)
    es_alt_endpoint_url = Column(String(512))
    es_endpoint_url = Column(String(512), nullable=False)
    index_rollover_policy_max_age_days = Column(Integer, default=7, nullable=False)
    index_rollover_policy_max_doc_count = Column(Integer, default=40000000, nullable=False)
    kbn_alt_endpoint_url = Column(String(512))
    kbn_endpoint_url = Column(String(512), nullable=False)
    last_known_good_enabled=Column(Boolean, default=True, nullable=False)
    retention_period = Column(Integer, default=30, nullable=False)
    transaction_id = Column(Integer, primary_key=True)
    updated_date = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class KibanaTemplate(Base):
    __tablename__ = 'kibana_template'

    kibanaEndpoint = Column(
        String(String(512)),
        primary_key=True,
        index=True,
        nullable=False
    )
    accountUid = Column(
        String(64),
        primary_key=True,
        index=True,
        nullable=False
    )
    objectId = Column(
        String(64),
        primary_key=True,
        index=True,
        nullable=False
    )

    type = Column(
        String(64),
        index=False,
        unique=False,
        nullable=False
    )
    releaseVersion = Column(
        String(64),
        index=False,
        unique=False,
        nullable=False
    )
    hash = Column(
        String(),
        index=False,
        unique=False,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        index=False,
        unique=False,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        index=False,
        unique=False,
        nullable=False
    )
    __table_args__ = (
        PrimaryKeyConstraint(
            accountUid, objectId, kibanaEndpoint
        ),
    )

    def __repr__(self):
        return '<KibanaTemplate kibanaEndpoint: %r accountUid: %r objectId: %r type: %r updated_at: %r>' \
               % (self.kibanaEndpoint, self.accountUid, self.objectId, self.type, self.updated_at)