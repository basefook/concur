import hashlib

from pyramid.view import view_config

from concur.db.models import Poll


@view_config(route_name='poll_view', renderer='poll.html')
def view_poll(req):
    name = req.matchdict['name'].lower()
    idx = req.matchdict['idx']
    h = hashlib.sha1(name.encode('utf-8'))
    key = '{}-{}'.format(h.hexdigest(), idx)
    print(key)
    poll = req.db.query(Poll)\
        .filter(Poll.key == key)\
        .first()
    if not poll:
        raise Exception() # TODO: redirect
    return {
        'title': 'concur - ' + poll.prompt[:32],
        'prompt': poll.prompt,
    }
