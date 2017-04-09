from tempfile import gettempdir
from os.path import join
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import *

if all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    db_path = "mysql+pymysql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
else:
    db_path = "sqlite:///" + join(gettempdir(), "ueberwachungspaket.db")

engine = create_engine(db_path, convert_unicode=True, pool_recycle=3600)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    if NO_DB:
        return
    from . import models
    Base.metadata.create_all(bind=engine)
