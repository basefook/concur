from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('.db')
    config.include('.auth')
    config.include('.api')
    config.include('.web')
    config.scan()
    return config.make_wsgi_app()
