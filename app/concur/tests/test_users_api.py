import pytest  # noqa

from concur.db.models import User, Grant # noqa


def test_get_user(app, test_context):
    """
    """
    resp = app.get('/users/{}'.format(test_context['user']['id']), headers={
        'authorization': 'Bearer {}'.format(test_context['grant']['access_token'])
    })
    assert resp.status_code == 200


def test_delete_user(app, test_context):
    """
    """
    resp = app.delete('/users/{}'.format(test_context['user']['id']), headers={
        'authorization': 'Bearer {}'.format(test_context['grant']['access_token'])
    })
    assert resp.status_code == 200
