import pytest  # noqa

from concur.db.models import User, Grant # noqa


def test_get_user(app, test_user_id):
    """
    """
    resp = app.get('/users/{}'.format(test_user_id))
    assert resp.status_code == 200


def test_delete_user(app, test_user_id):
    """
    """
    resp = app.delete('/users/{}'.format(test_user_id))
    assert resp.status_code == 200
