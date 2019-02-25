from sqlalchemy import Column, Integer, MetaData, create_engine, inspect
from sqlalchemy.exc import (IntegrityError, InvalidRequestError,
                            NoInspectionAvailable)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.serializer import dumps as sdumps, loads as sloads
from sqlalchemy.orm import Query, sessionmaker, scoped_session
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.pool import NullPool


def get_session(db_uri='sqlite://'):
    engine = create_engine(db_uri, poolclass=NullPool)
    metadata = MetaData(bind=engine)
    inspector = inspect(engine)
    Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=True, bind=engine,
                     query_cls=Query)
        )
    Session.metadata = metadata
    Session.inspector = inspect(engine)
    return Session()

def get_base():
    return declarative_base()
