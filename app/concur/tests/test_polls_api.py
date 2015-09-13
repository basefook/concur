import pytest  # noqa
import jsonschema

from .requests import create_poll, cast_vote


flag_create_poll_failed = False


def test_create_and_get_poll(app, test_context):
    global flag_create_poll_failed

    try:
        resp = create_poll(app, test_context['grant']['access_token'], "Are you happy?", ["yes", "no"])
    except:
        flag_create_poll_failed = True
        raise

    for k in ['id', 'prompt', 'options', 'is_public']:
        assert k in resp.json

    resp = app.get('/polls/{}'.format(resp.json['id']))

    for k in ['id', 'prompt', 'options', 'is_public']:
        assert k in resp.json


@pytest.mark.skipif('flag_create_poll_failed')
def test_cast_vote(app, test_context):
    resp = create_poll(app, test_context['grant']['access_token'], "Are you happy?", ["yes", "no"])

    option_id = resp.json['options'][0]['id']

    resp = cast_vote(app, test_context['grant']['access_token'], option_id)

    assert resp.status_code == 200

    jsonschema.validate(resp.json, {
        'type': 'object',
        'required': ['id', 'option', 'created_at', 'poll'],
        'properties': {
            'id': {'type': 'string'},
            'created_at': {'type': 'integer'},
            'option': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string'},
                    'tally': {'type': 'integer'},
                }
            },
            'poll': {
                'type': 'object',
                'required': ['id'],
                'properties': {
                    'id': {'type': 'string'}
                }
            }
        }
    })
