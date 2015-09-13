import threading
import pytz

from datetime import datetime
from collections import OrderedDict

from zope.interface import implementer
from pyramid.interfaces import ISession, ISessionFactory

from concur.db.models import User, Grant, GroupMembership
from concur.constants import RE_BEARER_AUTH_HEADER


class LRU_Cache(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.RLock()

    def concurrent(func):
        def locked(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return locked

    @concurrent
    def __contains__(self, key):
        return key in self.cache

    @concurrent
    def get(self, key, default=None):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return default

    @concurrent
    def pop(self, key, default=None):
        try:
            value = self.cache.pop(key)
            return value
        except KeyError:
            return default

    @concurrent
    def put(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value
        return value


@implementer(ISession)
class Session(object):
    grant_cache = LRU_Cache(capacity=5000)

    @classmethod
    def cache_grant_data(cls, grant):
        return {
            'access_token': grant.access_token,
            'user_id': grant.user_id,
            'expires_at': grant.expires_at,
            'created_at': grant.created_at,
        }

    @classmethod
    def extract_access_token(cls, req):
        auth_header = req.headers.get('authorization')
        if auth_header is not None:
            match = RE_BEARER_AUTH_HEADER.match(auth_header)
            if match:
                return match.groups()[0]
            else:
                # NOTE: unauthorized
                raise Exception('The provided access token is invalid.')
        return None

    @classmethod
    def fetch_password_grant(cls, req, access_token):
        grant = req.db\
            .query(Grant)\
            .filter_by(access_token=access_token)\
            .first()
        if grant is None:
            # NOTE: unauthorized
            raise Exception('The provided access token is invalid.')
        return grant

    def __init__(self, req):
        self.req = req

        # using access token in auth header, try to get oauth password grant
        # first from data; then try loading it from DB if not found in cache.
        access_token = self.extract_access_token(req)
        if access_token is not None:
            self.grant = None
            self.data = self.grant_cache.get(access_token)
            if self.data is None:
                grant = self.fetch_password_grant(req, access_token)
                self.data = self.cache_grant_data(grant)
                self.grant_cache.put(access_token, self.data)
            if self.data['expires_at'] <= datetime.now(pytz.utc):
                raise Exception('expired grant')
        else:
            self.grant = Grant.new_password_grant(
                None,  # user_id set by self.remember()
                req.user_agent,
                req.remote_addr)
            self.data = self.cache_grant_data(self.grant)

    def __iter__(self):
        return self.data.items()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        # TODO: make sure we either persist extra keys/values
        # or else we disalllow them.
        self.data[key] = value

    def remember(self, user):
        if self.grant is not None:
            self.grant.grantee = user
            self.data['user_id'] = user.id
            self.grant_cache.put(self.grant.access_token, self.data)
            self.req.db.add(self.grant)
        else:
            # cannot reassigned the grant
            raise Exception('Cannot reassign access token.')

    def invalidate(self):
        if self.new:
            self.grant.expires_at = datetime.now(pytz.utc)
        else:
            self.req.db\
                .query(Grant)\
                .filter_by(access_token=self.data['access_token'])\
                .update({Grant.expires_at: datetime.now(pytz.utc)})

    def changed(self):
        pass

    @property
    def new(self):
        return (self.grant is not None)

    @property
    def created(self):
        return self.data['created_at']

    @property
    def user(self):
        if self.new:
            return self.grant.grantee
        if not hasattr(self, '_user'):
            self._user = self.req.db\
                .query(User)\
                .filter_by(id=self.data['user_id'])\
                .first()
        return self._user

    @property
    def groups(self):
        if self.new:
            user = self.user
            return [g.id for g in user.groups] if user else []
        if not hasattr(self, '_groups'):
            self._groups = self.req.db\
                .query(GroupMembership.group_id)\
                .filter_by(user_id=self.user.id)\
                .all()
        return self._groups


@implementer(ISessionFactory)
class SessionFactory(object):
    def __call__(self, request):
        session = Session(request)
        return session
