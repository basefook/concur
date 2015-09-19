from pyramid.view import view_config, view_defaults
from jsonschema import (
    ValidationError as JsonValidationError,
    validate as validate_json
)

from concur.api.contexts import BaseContext
from concur.api import exceptions as exc


class View(object):
    def __init__(self, context, request):
        self.req = request
        self.db = request.db
        self.ctx = context


def login_required_decorator(func):
    def wrapper(self, *args, **kwargs):
        if isinstance(self, BaseContext) and self.req.session.new:
            raise exc.Unauthorized('login required')  # unauthorized
        return func(self, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def api_defaults(context=None, login_required=True, *args, **kwargs):
    return view_defaults(renderer='json', context=context, *args, **kwargs)


def api_config(login_required=True, *args, **kwargs):
    decorators = []
    if login_required:
        decorators.append(login_required_decorator)
    return view_config(decorator=decorators, *args, **kwargs)


class json_body(object):
    """ Json request body validator view decorator.
    """
    memoized_schemas = {}

    def __init__(self, doc_class, role=None):
        self.doc_class = doc_class
        self.role = role

    def __call__(self, func):
        doc_class = self.doc_class
        role = self.role

        def json_validator(self):
            try:
                cache_key = '{}:{}'.format(doc_class, role)
                json_schema = json_body.memoized_schemas.get(cache_key)
                if not json_schema:
                    json_schema = doc_class.get_schema(role=role)
                    json_body.memoized_schemas[cache_key] = json_schema
                validate_json(self.req.json, json_schema)
            except ValueError:
                raise exc.ValidationError()
            except JsonValidationError:
                raise exc.ValidationError()
            return func(self)
        json_validator.__name__ = func.__name__
        return json_validator
