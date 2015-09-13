import os
import pytest
import transaction
import sqlalchemy as sa  # noqa

from random import choice
from string import ascii_letters as letters

from pyramid import testing  # noqa
from unittest.mock import MagicMock  # noqa
from paste.deploy import appconfig, loadapp
from webtest import TestApp

from concur.auth.session import SessionFactory
from concur.db.models import User, Grant
from concur.db.types import PUBLIC_ID
from concur.db.util import scoped_session, quick_sessionmaker

DEV_INI_FNAME = 'development.ini'


@pytest.fixture(scope='session')
def settings_path():
    path = os.path.split(os.path.abspath(__file__))[0]
    while DEV_INI_FNAME not in os.listdir(path):
        path = os.path.split(path)[0]
        if path == '/':
            raise Exception('{} not found.'.format(DEV_INI_FNAME))
    return path


@pytest.fixture(scope='session')
def settings(settings_path):
    config_path = 'config:{}'.format(DEV_INI_FNAME)
    settings = appconfig(config_path, 'main', relative_to=settings_path)
    return settings


@pytest.fixture(scope='session')
def app(settings_path):
    config_path = 'config:{}'.format(DEV_INI_FNAME)
    app = loadapp(config_path, relative_to=settings_path)
    test_app = TestApp(app)
    test_app.registry = app.registry
    return test_app


@pytest.yield_fixture(scope='function')
def app_db_session(app):
    db_session = app.registry.DB_Session()
    yield db_session
    transaction.abort()


@pytest.yield_fixture(scope='function')
def db_session(app):
    db_session = quick_sessionmaker()()
    yield db_session
    db_session.rollback()
    db_session.close()


@pytest.fixture(scope='function')
def session_factory(app, db_session):
    return SessionFactory()


@pytest.fixture(scope='module')
def test_context(request):
    with scoped_session(quick_sessionmaker()) as db_session:
        email = ''.join(choice(letters) for i in range(10)) + '@test.com'

        # use a fixed user id, since this would
        # otherwise change in each test function.
        user = User(email=email, password='test')
        user.id = PUBLIC_ID.next_id()

        grant = Grant.new_password_grant(user, 'user-agent', '0.0.0.0')

        db_session.add(user)
        db_session.add(grant)

        return {
            'user': user.__json__(),
            'grant': grant.__json__(),
        }


@pytest.fixture(scope='function')
def anon_request(app, db_session):
    request = app.RequestClass.blank('/api/v1/users')
    request.db_session = db_session
    return request


@pytest.fixture(scope='function')
def anon_session(anon_request):
    return SessionFactory()(anon_request)
