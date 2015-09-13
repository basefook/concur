import sqlalchemy as sa

from pyramid.security import Allow, Deny, Everyone  # noqa
from concur.db.models import User, Poll, Option, Vote, Grant
from concur.auth.constants import PERMISSIONS


class BaseContext(object):
    def __init__(self, request):
        self.req = request
        self.db = request.db


class GrantContext(BaseContext):
    def __init__(self, request):
        super(GrantContext, self).__init__(request)
        grant_id = self.req.matchdict['grant_id']
        self.grant = self.db.query(Grant)\
            .filter(Grant.id == grant_id,
                    Grant.deleted_at == sa.sql.null())\
            .first()
        if not self.grant:
            raise Exception('grant not found')

    def __acl__(self):
        return [
            (Allow, self.grant.grantee.id, PERMISSIONS.READ),
            (Allow, self.grant.grantee.id, PERMISSIONS.DELETE),
        ]


class UserContext(BaseContext):
    def __init__(self, request):
        super(UserContext, self).__init__(request)
        user_id = self.req.matchdict['user_id']
        self.user = self.db.query(User)\
            .filter(User.id == user_id,
                    User.deleted_at == sa.sql.null())\
            .first()
        if not self.user:
            raise Exception('user not found')

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


class OptionContext(BaseContext):
    def __init__(self, request):
        super(OptionContext, self).__init__(request)
        poll_id = self.req.matchdict['poll_id']
        option_id = self.req.matchdict['option_id']
        data = self.db.query(Poll, Option)\
            .filter(Poll.id == poll_id,
                    Poll.deleted_at == sa.sql.null())\
            .outerjoin(Option, Option.id == option_id)
        if not data:
            raise Exception()
        self.poll = data[0]
        self.option = data[1]
        if not self.option:
            raise Exception()

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
