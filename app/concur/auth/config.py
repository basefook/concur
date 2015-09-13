from pyramid.authorization import ACLAuthorizationPolicy
from .policy import SessionAuthenticationPolicy
from .session import SessionFactory


def includeme(config):
    config.set_session_factory(SessionFactory())
    config.set_authentication_policy(SessionAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())
