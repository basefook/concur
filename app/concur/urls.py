from concur.renderer import json_renderer
from concur.contexts import (
    GrantContext,
    UserContext,
    PollContext,
    OptionContext,
    VoteContext,
)


def includeme(config):
    routes = {
        'grants': {
            'pattern': '/grants'
        },
        'grant': {
            'pattern': '/grants/{grant_id:.+}',
            'context': GrantContext,
        },

        'users': {
            'pattern': '/users'
        },
        'user': {
            'pattern': '/users/{user_id:.+}',
            'context': UserContext,
        },

        'polls': {
            'pattern': '/polls',
        },
        'poll': {
            'pattern': '/polls/{poll_id:.+}',
            'context': PollContext,
        },

        'options': {
            'pattern': '/polls/{poll_id:.+}/options',
        },
        'option': {
            'pattern': '/polls/{poll_id:.+}/options/{option_id:.+}',
            'context': OptionContext,
        },

        'votes': {
            'pattern': '/votes',
        },
        'vote': {
            'pattern': '/votes/{vote_id:.+}',
            'context': VoteContext,
        },
    }

    for name, params in routes.items():
        context = params.get('context')
        config.add_route(name, params['pattern'], factory=context)

    config.add_renderer('json', json_renderer())
