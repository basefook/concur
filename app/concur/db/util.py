from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from concur.constants import DATABASE_URL


def quick_sessionmaker(echo=False):
    return sessionmaker(bind=create_engine(DATABASE_URL, echo=echo))


@contextmanager
def scoped_session(session_class):
    session = session_class()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
