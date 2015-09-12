from pyramid.view import view_config, view_defaults as _view_defaults  # noqa
from jsonschema import (
    ValidationError as JsonValidationError,
    validate as validate_json
)


class View(object):
    def __init__(self, context, request):
        self.req = request
        self.ctx = context
        self.db = request.db


def view_defaults(*args, **kwargs):
    return _view_defaults(renderer='json', *args, **kwargs)


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
                raise Exception  # TODO: raise proper API exception
            except JsonValidationError:
                raise Exception  # TODO raise proper API exception
            return func(self)
        json_validator.__name__ = func.__name__
        return json_validator
