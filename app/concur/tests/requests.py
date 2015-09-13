from random import choice
from string import ascii_letters as letters


def signup(app, email=None, password=None):
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


def logout(app, access_token, grant_id):
    return app.delete('/grants/{}'.format(grant_id), headers={
        'authorization': 'Bearer {}'.format(access_token)
    })


def create_poll(app, access_token, prompt, options):
    return app.post_json('/polls', {
        'prompt': prompt,
        'options': [{'text': text} for text in options],
    }, headers={
        'authorization': 'Bearer {}'.format(access_token)
    })


def cast_vote(app, access_token, option_id):
    return app.post_json('/votes', {
        'option_id': option_id,
    }, headers={
        'authorization': 'Bearer {}'.format(access_token)
    })
