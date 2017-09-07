import atexit

from tempfile import gettempdir
from os.path import join
from sqlalchemy import create_engine, exc, event, select
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

if all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    db_path = "mysql+pymysql://{}:{}@{}/{}?charset=utf8".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
else:
    db_path = "sqlite:///" + join(gettempdir(), "ueberwachungspaket.db")

engine = create_engine(db_path, convert_unicode=True, pool_recycle=3600)
atexit.register(lambda engine: engine.dispose(), engine)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)


@event.listens_for(engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        return

    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        if err.connection_invalidated:
            connection.scalar(select([1]))
        else:
            raise
    finally:
        connection.should_close_with_result = save_should_close_with_result
