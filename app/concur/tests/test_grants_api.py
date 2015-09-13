import pytest  # noqa

from random import choice
from string import ascii_letters as letters

from concur.db.models import User, Grant  # noqa


flag_signup_failed = False
flag_login_failed = False


def test_signup(app):
    global flag_signup_failed

    """Verify that user signup and login via oauth2 password grant works
        normally.
    """
    try:
        resp = create_user(app)
        assert resp.status_code == 200

        user_json = resp.json
        for k in ['email', 'created_at']:
            assert k in user_json
    except:
        flag_signup_failed = True
        raise


@pytest.mark.skipif('flag_signup_failed')
def test_login(app):
    global flag_login_failed
    try:
        resp = create_user(app)
        resp = login(app, resp.json['email'])
        assert resp.status_code == 200
        for k in ['access_token', 'expires_at', 'id']:
            assert k in resp.json
    except:
        flag_login_failed = True
        raise


@pytest.mark.skipif('flag_login_failed')
def test_logout(app):
    """
    """
    resp = create_user(app)
    resp = login(app, resp.json['email'])
    resp = logout(app, resp.json['id'])
    assert resp.status_code == 200


def create_user(app, email=None, password=None):
    if not email:
        email = ''.join(choice(letters) for i in range(10)) + '@test.com'
    if not password:
        password = 'test'
    return app.post_json('/users', {
        'email': email,
        'password': password,
    })


def login(app, email):
    return app.post_json('/grants', {
        'type': 'password',
        'email': email,
        'password': 'test',
    })


def logout(app, grant_id):
    return app.delete('/grants/{}'.format(grant_id))
