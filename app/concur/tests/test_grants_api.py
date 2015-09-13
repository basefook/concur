import pytest  # noqa

from concur.db.models import User, Grant  # noqa

from .requests import login, logout, signup


flag_signup_failed = False


def test_signup(app):
    global flag_signup_failed

    """Verify that user signup and login via oauth2 password grant works
        normally.
    """
    try:
        resp = signup(app)
        assert resp.status_code == 200

        user_json = resp.json
        for k in ['email', 'created_at']:
            assert k in user_json
    except:
        flag_signup_failed = True
        raise


@pytest.mark.skipif('flag_signup_failed')
def test_login(app):
    resp = signup(app)
    resp = login(app, resp.json['email'])
    assert resp.status_code == 200
    for k in ['access_token', 'expires_at', 'id', 'type']:
        assert k in resp.json


def test_logout(app, test_context):
    """
    """
    resp = logout(app,
                  test_context['grant']['access_token'],
                  test_context['grant']['id'])
    assert resp.status_code == 200
