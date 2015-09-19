from pyramid.httpexceptions import HTTPException


class ApiException(HTTPException):
    api_status_string = None
    default_message = "API error"
    http_status_int = 200
    info_url = ''

    def __init__(self, message=None, data=None):
        super(ApiException, self).__init__()
        self.status_int = self.http_status_int
        self.message = message or self.default_message
        self.data = data or {}

    def __json__(self, request=None):
        return {
            'code': self.api_status_string,
            'status': self.http_status_int,
            'message': self.message,
            'info': self.info_url,
            'data': self.data,
        }


class NotFound(ApiException):
    default_message = "resource not found"
    api_status_string = 'not_found'
    http_status_int = 404


class Unauthorized(ApiException):
    default_message = "access denied"
    api_status_string = 'unauthorized'
    http_status_int = 401


class Forbidden(ApiException):
    default_message = "cannot auhorize user"
    api_status_string = 'fobidden'
    http_status_int = 403


class ValidationError(ApiException):
    default_message = "request validation error"
    api_status_string = 'validation_error'
    http_status_int = 400

    def __init__(self, message=None, fields=None):
        super(ValidationError, self).__init__(message=message, data=fields)


class Conflict(ApiException):
    default_message = 'conflicting resources'
    api_status_string = 'conflict'
    http_status_int = 409


class NotSupported(ApiException):
    default_message = 'request not supported'
    api_status_string = 'not_supported'
    http_status_int = 400
