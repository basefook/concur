import time
import pytest  # noqa
import jsonschema

from .requests import create_poll, cast_vote, add_option


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
def test_get_poll_from_static_url(app, test_context):
    resp = create_poll(app, test_context['grant']['access_token'], "Are you happy?", ["yes", "no"])
    poll_static_url = resp.json['url']

    resp = app.get(poll_static_url, status='*')
    assert resp.status_code == 200


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


@pytest.mark.skipif('flag_create_poll_failed')
def test_add_poll_option(app, test_context):
    resp = create_poll(app, test_context['grant']['access_token'], "Are you happy?", ["yes", "no"])
    poll_id = resp.json['id']

    resp = add_option(app, test_context['grant']['access_token'], poll_id, {'text': 'maybe'})
    assert resp.status_code == 200
    jsonschema.validate(resp.json, {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'text': {'type': 'string'},
            'tally': {'type': 'integer'},
        }
    })
