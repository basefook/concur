from sqlalchemy.orm import Bundle

from concur.db.models import User, Poll, Option, Vote


class BaseContext(object):
    def __init__(self, request):
        self.req = request
        self.db = request.db
        self.on_create()

    def on_create(self):
        pass


class UserContext(BaseContext):
    def on_create(self):
        user_id = self.req.matchdict['user_id']
        self.user = self.db.query(User).filter(id=user_id).first()


class PollContext(BaseContext):
    def on_create(self):
        poll_id = self.req.matchdict['poll_id']
        self.poll = self.db.query(Poll).filter(id=poll_id).first()


class OptionContext(BaseContext):
    def on_create(self):
        poll_id = self.req.matchdict['poll_id']
        option_id = self.req.matchdict['option_id']
        data = self.db.query(Poll, Option)\
            .filter(Poll.id == poll_id)\
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
        self.vote = self.db.query(Vote).filter(id=vote_id).first()
        self.poll = self.vote.poll
