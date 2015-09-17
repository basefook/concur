def includeme(config):
    config.add_route('poll_view', '/poll/{name}/{idx}')
