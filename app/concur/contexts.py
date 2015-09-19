import sqlalchemy as sa

from pyramid.security import Allow, Deny, Everyone  # noqa
from concur.db.models import User, Poll, Option, Vote, Grant
from concur.auth.constants import PERMISSIONS

from concur.api import exceptions as exc


class BaseContext(object):
    def __init__(self, request):
        self.req = request
        self.db = request.db


class GrantsContext(BaseContext):
    def __init__(self, request):
        super(GrantsContext, self).__init__(request)
        self.grantee = self.db.query(User)\
            .filter(User.email == self.req.json['email'])\
            .first()
        if not self.grantee:
            raise exc.Unauthorized()


class GrantContext(BaseContext):
    def __init__(self, request):
        super(GrantContext, self).__init__(request)
        grant_id = self.req.matchdict['grant_id']
        self.grant = self.db.query(Grant)\
            .filter(Grant.id == grant_id,
                    Grant.deleted_at == sa.sql.null())\
            .first()
        if not self.grant:
            raise exc.NotFound('grant not found')

    def __acl__(self):
        return [
            (Allow, self.grant.grantee.id, PERMISSIONS.READ),
            (Allow, self.grant.grantee.id, PERMISSIONS.DELETE),
        ]


class UsersContext(BaseContext):
    def __init__(self, request):
        super(UsersContext, self).__init__(request)
        email = self.req.json['email']
        password = self.req.json['password']
        self.user = self.db.query(User).filter(User.email == email).first()


class UserContext(BaseContext):
    def __init__(self, request):
        super(UserContext, self).__init__(request)
        user_id = self.req.matchdict['user_id']
        self.user = self.db.query(User)\
            .filter(User.id == user_id,
                    User.deleted_at == sa.sql.null())\
            .first()
        if not self.user:
            raise exc.NotFound('user not found')

    def __acl__(self):
        return [
            (Allow, self.user.group_id, PERMISSIONS.READ),
            (Allow, self.user.id, PERMISSIONS.READ),
            (Allow, self.user.id, PERMISSIONS.UPDATE),
            (Allow, self.user.id, PERMISSIONS.DELETE),
        ]


class PollContext(BaseContext):
    def __init__(self, request):
        super(PollContext, self).__init__(request)
        poll_id = self.req.matchdict['poll_id']
        self.poll = self.db.query(Poll)\
            .filter(Poll.id == poll_id,
                    Poll.deleted_at == sa.sql.null())\
            .first()

    def __acl__(self):
        return [
            (Allow, Everyone, PERMISSIONS.READ),
            (Allow, self.poll.creator.id, PERMISSIONS.UPDATE),
            (Allow, self.poll.creator.id, PERMISSIONS.DELETE),
        ]


class PollOptionsContext(BaseContext):
    def __init__(self, request):
        super(PollOptionsContext, self).__init__(request)
        poll_id = self.req.matchdict['poll_id']
        self.poll = self.db.query(Poll)\
            .filter(Poll.id == poll_id, Poll.deleted_at == sa.sql.null())\
            .first()
        if not self.poll:
            raise exc.NotFound('poll not found')

    def __acl__(self):
        return [
            (Allow, Everyone, PERMISSIONS.READ),
        ]



class PollOptionContext(BaseContext):
    def __init__(self, request):
        super(PollOptionContext, self).__init__(request)
        poll_id = self.req.matchdict['poll_id']
        option_id = self.req.matchdict['option_id']
        data = self.db.query(Poll, Option)\
            .filter(Poll.id == poll_id,
                    Poll.deleted_at == sa.sql.null())\
            .outerjoin(Option, Option.id == option_id)
        if not data:
            raise exc.NotFound('poll not found')
        self.poll = data[0]
        self.option = data[1]
        if not self.option:
            raise exc.NotFound('poll options not found')

    def __acl__(self):
        return [
            (Allow, Everyone, PERMISSIONS.READ),
        ]


class VoteContext(BaseContext):
    def __init__(self, request):
        super(VoteContext, self).__init__(request)
        vote_id = self.req.matchdict['vote_id']
        self.vote = self.db.query(Vote)\
            .filter(Vote.id == vote_id,
                    Vote.deleted_at == sa.sql.null())\
            .first()
        self.poll = self.vote.poll

    def __acl__(self):
        return [
            (Allow, self.vote.voter, PERMISSIONS.READ),
        ]
