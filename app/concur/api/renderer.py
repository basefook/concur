from uuid import UUID
from pyramid.renderers import JSON
from datetime import datetime, timedelta

from concur.util import to_timestamp


def includeme(config):
    config.add_renderer('json', json_renderer())


def json_renderer():
    def datetime_adapter(dt, req):
        return to_timestamp(dt)

    def timedelta_adapter(delta, req):
        return delta.total_seconds()

    def uuid_adapter(uuid, req):
        return str(uuid)

    json_renderer = JSON()
    json_renderer.add_adapter(datetime, datetime_adapter)
    json_renderer.add_adapter(UUID, uuid_adapter)
    json_renderer.add_adapter(timedelta, timedelta_adapter)

    return json_renderer
