import sqlalchemy as sa
import pytest  # noqa

from random import choice
from string import ascii_letters as letters

from concur.db.models import User, Grant  # noqa

from .requests import login, logout, signup


flag_signup_failed = False


def test_signup(app, db_session):
    global flag_signup_failed

    """Verify that user signup and login via oauth2 password grant works
        normally.
    """
    try:
        resp = signup(app, db_session)
        assert resp.status_code == 200
        for k in ['email', 'created_at']:
            assert k in resp.json
    except:
        flag_signup_failed = True
        raise


@pytest.mark.skipif('flag_signup_failed')
def test_verify_email(app, db_session):
    email = ''.join(choice(letters) for i in range(10)) + '@test.com'
    password = 'test'
    resp = app.post_json('/users', {
        'email': email,
        'password': password,
    })
    code = db_session\
        .query(User.verification_code)\
        .filter(User.id == resp.json['id'])\
        .scalar()
    resp = app.get('/users/{}/verify?code={}'.format(resp.json['id'], code))
    assert resp.json['success']


@pytest.mark.skipif('flag_signup_failed')
def test_login(app, db_session):
    resp = signup(app, db_session)
    resp = login(app, resp.json['email'])
    assert resp.status_code == 200
    for k in ['access_token', 'expires_at', 'id', 'type']:
        assert k in resp.json


def test_logout(app, test_context):
    resp = logout(app,
                  test_context['grant']['access_token'],
                  test_context['grant']['id'])
    assert resp.status_code == 200
