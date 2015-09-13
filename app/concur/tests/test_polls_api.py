import pytest  # noqa

from concur.db.models import Poll, Option

from .requests import create_poll


def test_create_and_get_poll(app, db_session, test_context):
    """
    """
    resp = create_poll(app, test_context['grant']['access_token'], "Are you happy?", ["yes", "no"])

    for k in ['id', 'prompt', 'options', 'is_public']:
        assert k in resp.json

    resp = app.get('/polls/{}'.format(resp.json['id']))

    for k in ['id', 'prompt', 'options', 'is_public']:
        assert k in resp.json

    db_session.query(Option).filter_by(poll_id=resp.json['id']).delete()
    db_session.query(Poll).filter_by(id=resp.json['id']).delete()
    db_session.commit()
