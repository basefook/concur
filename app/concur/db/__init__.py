from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register


def includeme(config):
    from . import models

    settings = config.get_settings()
    engine = engine_from_config(settings, prefix='sqlalchemy.', echo=False)

    models.Base.metadata.bind = engine
    models.Base.metadata.create_all(engine)

    add_db_session_request_method(config, engine, use_tm=True)


def add_db_session_request_method(config, engine, use_tm=True):
    config.registry.DB_Session = sessionmaker(bind=engine)
    if use_tm:
        # add sqlalchemy session to active transaction
        register(config.registry.DB_Session)

    def dbs(request):
        return config.registry.DB_Session()

    config.add_request_method(dbs, reify=True)
