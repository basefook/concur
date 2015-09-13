import sqlalchemy as sa

from concur.db.models import User, Poll, Option, Vote, Grant


class BaseContext(dict):
    def __init__(self, request):
        self.req = request
        self.db = request.db
        self.on_create()

    def on_create(self):
        pass


class UserContext(BaseContext):
    def on_create(self):
        user_id = self.req.matchdict['user_id']
        self.user = self.db.query(User)\
            .filter(User.id == user_id,
                    User.deleted_at == sa.sql.null())\
            .first()
        if not self.user:
            raise Exception('user not found')


class PollContext(BaseContext):
    def on_create(self):
        poll_id = self.req.matchdict['poll_id']
        self.poll = self.db.query(Poll)\
            .filter(Poll.id == poll_id,
                    Poll.deleted_at == sa.sql.null())\
            .first()


class OptionContext(BaseContext):
    def on_create(self):
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


class VoteContext(BaseContext):
    def on_create(self):
        vote_id = self.req.matchdict['vote_id']
        self.vote = self.db.query(Vote)\
            .filter(Vote.id == vote_id,
                    Vote.deleted_at == sa.sql.null())\
            .first()
        self.poll = self.vote.poll


class GrantContext(BaseContext):
    def on_create(self):
        grant_id = self.req.matchdict['grant_id']
        self.grant = self.db.query(Grant)\
            .filter(Grant.id == grant_id,
                    Grant.deleted_at == sa.sql.null())\
            .first()
        if not self.grant:
            raise Exception('grant not found')
