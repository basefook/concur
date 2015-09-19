import re

PATTERNS = {
    'UUID': r'[a-fA-F0-9]{32}'
}


def pattern(path):
    crumbs = []
    for x in path.lstrip('/').split('/'):
        m = re.match(r'\{(.+):(.+)\}', x)
        if m:
            name, regexp_name = m.groups()
            x = '{' + name + ':' + PATTERNS[regexp_name] + '}'
        crumbs.append(x)
    return '/' + '/'.join(crumbs)


def includeme(config):
    from .contexts import (
        GrantsContext,
        GrantContext,
        UserContext,
        UsersContext,
        PollContext,
        PollOptionContext,
        PollOptionsContext,
        VoteContext,
    )

    routes = {
        'grants': {
            'pattern': '/grants',
            'context': GrantsContext,
        },
        'grant': {
            'pattern': pattern('/grants/{grant_id:UUID}'),
            'context': GrantContext,
        },

        'users': {
            'pattern': '/users',
            'context': UsersContext,
        },
        'user': {
            'pattern': pattern('/users/{user_id:UUID}'),
            'context': UserContext,
        },

        'verify_user': {
            'pattern': pattern('/users/{user_id:UUID}/verify'),
            'context': UserContext,
        },

        'polls': {
            'pattern': '/polls',
        },
        'poll': {
            'pattern': pattern('/polls/{poll_id:UUID}'),
            'context': PollContext,
        },

        'poll_options': {
            'pattern': pattern('/polls/{poll_id:UUID}/options'),
            'context': PollOptionsContext,
        },
        'poll_option': {
            'pattern': pattern('/polls/{poll_id:UUID}/options/{option_id:UUID}'),
            'context': PollOptionContext,
        },

        'votes': {
            'pattern': '/votes',
        },
        'vote': {
            'pattern': pattern('/votes/{vote_id:UUID}'),
            'context': VoteContext,
        },
    }

    for name, params in routes.items():
        context = params.get('context')
        config.add_route(name, params['pattern'], factory=context)
