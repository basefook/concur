import sqlalchemy as sa  # noqa

from random import choice
from string import ascii_letters as letters

from concur.db.models import User


def signup(app, db_session, email=None, password=None):
    if not email:
        email = ''.join(choice(letters) for i in range(10)) + '@test.com'
    if not password:
        password = 'test'
    resp = app.post_json('/users', {
        'email': email,
        'password': password,
    }, status='*')
    code = db_session\
        .query(User.verification_code)\
        .filter(User.id == resp.json['id'])\
        .scalar()
    app.get('/users/{}/verify?code={}'.format(resp.json['id'], code), status='*')
    return resp


def login(app, email):
    return app.post_json('/grants', {
        'type': 'password',
        'email': email,
        'password': 'test',
    }, status='*')


def logout(app, access_token, grant_id):
    return app.delete('/grants/{}'.format(grant_id), headers={
        'authorization': 'Bearer {}'.format(access_token)
    }, status='*')


def create_poll(app, access_token, prompt, options):
    return app.post_json('/polls', {
        'prompt': prompt,
        'options': [{'text': text} for text in options],
    }, headers={
        'authorization': 'Bearer {}'.format(access_token)
    }, status='*')


def cast_vote(app, access_token, option_id):
    return app.post_json('/votes', {
        'option_id': option_id,
    }, headers={
        'authorization': 'Bearer {}'.format(access_token)
    }, status='*')


def add_option(app, access_token, poll_id, option):
    return app.post_json('/polls/{}/options'.format(poll_id), option, headers={
        'authorization': 'Bearer {}'.format(access_token)
    }, status='*')
